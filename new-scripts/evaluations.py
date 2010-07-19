#! /usr/bin/env python
'''
Module that permits evaluating experiments conducted with experiments.py
'''

from __future__ import with_statement

import os
import sys
import shutil
import re
import ast
from optparse import OptionParser
from glob import glob
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(levelname)-8s %(message)s',)
                    
import tools


def convert_to_correct_type(val):
    '''
    Safely evaluate an expression node or a string containing a Python expression. 
    The string or node provided may only consist of the following Python literal 
    structures: strings, numbers, tuples, lists, dicts, booleans, and None.
    '''
    try:
        val = ast.literal_eval(val)
    except (ValueError, SyntaxError):
        pass
    return val
      
      

class EvalOptionParser(OptionParser):
    def __init__(self, *args, **kwargs):
        OptionParser.__init__(self, option_class=tools.ExtOption, *args, **kwargs)
        
        self.add_option(
            "-s", "--source", action="store", dest="exp_dir", default="",
            help="path to experiment directory")
        self.add_option(
            "-d", "--dest", action="store", dest="eval_dir", default="",
            help="path to evaluation directory (default: <exp_dir>-eval)")
        
    def error(self, msg):
        '''Show the complete help AND the error message'''
        self.print_help()
        OptionParser.error(self, msg)
        
    def parse_options(self):
        options, args = self.parse_args()
        
        if not options.exp_dir:
            raise self.error('You need to specify an experiment directory')
        options.exp_dir = os.path.normpath(os.path.abspath(options.exp_dir))
        logging.info('Exp dir:  "%s"' % options.exp_dir)
        if not os.path.isdir(options.exp_dir):
            raise self.error('"%s" is no directory' % options.exp_dir)
        
        if not options.eval_dir:
            parent_dir = os.path.dirname(options.exp_dir)
            dir_name = os.path.basename(options.exp_dir)
            options.eval_dir = os.path.join(parent_dir, dir_name + '-eval')
            logging.info('Eval dir: "%s"' % options.eval_dir)
        
        return options
        
    

class Evaluation(object):
    '''
    Base class for all evaluations
    '''
    
    def __init__(self, parser=EvalOptionParser()):
        self.parser = parser
        options = self.parser.parse_options()
        # Give all the options to the experiment instance
        self.__dict__.update(options.__dict__)
        
    def evaluate(self):
        raise Exception('Not Implemented')
        
    def _get_run_dirs(self):
        run_dirs = glob(os.path.join(self.exp_dir, 'runs-*-*', '*'))
        return run_dirs
        
        
        
class CopyEvaluation(Evaluation):
    '''
    Evaluation that copies files from run dirs into a new tree under
    <eval-dir> according to the value "id" in the run's properties file
    '''
    def __init__(self, *args, **kwargs):
        Evaluation.__init__(self, *args, **kwargs)
        
        # Save the newly created run dirs for further evaluation
        self.dirs = []
        
    def evaluate(self):
        copy_dict = {}
        
        run_dirs = self._get_run_dirs()
        for run_dir in run_dirs:
            prop_file = os.path.join(run_dir, 'properties')
            props = tools.Properties(prop_file)
            id = props.get('id')
            dest = os.path.join(self.eval_dir, *id)
            copy_dict[run_dir] = dest
            
        self.dirs = copy_dict.values()
            
        for source, dest in copy_dict.items():
            tools.updatetree(source, dest)
        
        
    
class Pattern(object):
    def __init__(self, name, regex_string, group, file, required):
        self.name = name
        self.regex = re.compile(regex_string)
        self.group = group
        self.file = file
        self.required = required
        
    def __str__(self):
        return self.regex.pattern
        
        

class ParseEvaluation(CopyEvaluation):
    '''
    Evaluation that parses various files and writes found results
    into the run's properties file
    '''
    def __init__(self, *args, **kwargs):
        CopyEvaluation.__init__(self, *args, **kwargs)
        
        self.patterns = defaultdict(list)
        self.functions = defaultdict(list)
        
        
    def add_pattern(self, name, regex_string, group=1, file='run.log', required=True):
        '''
        During evaluate() look for pattern in file and add what is found in group
        to the properties dictionary under "name"
        
        properties[name] = re.compile(regex_string).search(file_content).group(group)
        
        If required is True and the pattern is not found in file, an error
        message is printed
        '''
        pattern = Pattern(name, regex_string, group, file, required)
        self.patterns[file].append(pattern)
        
    def add_key_value_pattern(self, name, file='run.log'):
        '''
        Convenience method that adds a pattern for lines containing only a
        key:value pair
        '''
        regex_string = r'\s*%s\s*[:=]\s*(.+)' % name
        self.add_pattern(name, regex_string, 1, file)
        
        
    def add_function(self, function, file='run.log'):
        '''
        After all the patterns have been evaluated and the found values have
        been inserted into the properties files, call function(file_content, props)
        for each added function.
        The function is supposed to return a dictionary with new properties.
        '''
        self.functions[file].append(function)
        
        
    def evaluate(self):
        CopyEvaluation.evaluate(self)
        
        for run_dir in self.dirs:
            prop_file = os.path.join(run_dir, 'properties')
            props = tools.Properties(prop_file)
            for file, patterns in self.patterns.items():
                file = os.path.join(run_dir, file)
                new_props = self._parse_file(file, patterns)
                props.update(new_props)
            for file, functions in self.functions.items():
                file = os.path.join(run_dir, file)
                new_props = self._apply_functions(file, functions, props)
                props.update(new_props)
            props.write()
            
            
    def _parse_file(self, file, patterns):
        found_props = {}
        
        if not os.path.exists(file):
            logging.error('File "%s" does not exist' % file)
            return found_props
        
        content = open(file).read()
        
        for pattern in patterns:
            match = pattern.regex.search(content)
            if match:
                try:
                    value = match.group(pattern.group)
                    value = convert_to_correct_type(value)
                    found_props[pattern.name] = value
                except IndexError:
                    msg = 'Group "%s" not found for pattern "%s" in file "%s"'
                    msg %= (pattern.group, pattern, file)
                    logging.error(msg)
            elif pattern.required:
                logging.error('Pattern "%s" not present in file "%s"' % (pattern, file))
        return found_props
        
        
    def _apply_functions(self, file, functions, old_props):
        new_props = {}
        
        if not os.path.exists(file):
            logging.error('File "%s" does not exist' % file)
            return {}
        
        content = open(file).read()
        
        for function in functions:
            new_props.update(function(content, old_props))
        return new_props
        
        
        
def build_evaluator(parser=EvalOptionParser()):
    eval = ParseEvaluation(parser)
    eval.add_key_value_pattern('run start time')
    eval.add_pattern('initial h value', r'Initial state h value: (\d+)', required=False)
    eval.add_pattern('plan length', r'Plan length: (\d+)')
    eval.add_pattern('expanded', r'Expanded (\d+)')
    eval.add_pattern('generated', r'Generated (\d+)')
    eval.add_pattern('search time', r'Search time: (.+)s')
    eval.add_pattern('total time', r'Total time: (.+)s')
    
    def completely_explored(content, old_props):
        new_props = {}
        if 'Completely explored state space -- no solution!' in content:
            new_props['completely explored'] = True
        return new_props
    
    def get_status(content, old_props):
        new_props = {}
        if 'does not support' in content:
            new_props['status'] = 'unsupported'
        elif 'plan length' in old_props:
            new_props['status'] = 'ok'
        elif 'completely explored' in old_props:
            new_props['status'] = 'failure'
        else:
            new_props['status'] = 'not ok'
        return new_props
        
    eval.add_function(completely_explored)
    eval.add_function(get_status)
    return eval


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print 'Testing'
        sys.argv.extend('-s test'.split())
        
    eval = build_evaluator()
    eval.evaluate()
    
