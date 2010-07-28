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
from external import argparse


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
      
      

class EvalOptionParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        argparse.ArgumentParser.__init__(self, *args, 
                formatter_class=argparse.ArgumentDefaultsHelpFormatter, **kwargs)
                
        def directory(string):
            if not os.path.isdir(string):
                msg = "%r is not an evaluation directory" % string
                raise argparse.ArgumentTypeError(msg)
            return string
        
      
        self.add_argument('exp_dirs', nargs='+',
                help='path to experiment directory', type=directory)
        
        self.add_argument('-d', '--dest', dest='eval_dir', default='',
                help='path to evaluation directory (default: <exp_dirs>-eval)')
            
    
    def parse_args(self):
        args = argparse.ArgumentParser.parse_args(self)
        
        args.exp_dirs = map(lambda dir: os.path.normpath(os.path.abspath(dir)), args.exp_dirs)
        logging.info('Exp dirs: "%s"' % args.exp_dirs)
        
        if not args.eval_dir:
            parent_dir = os.path.dirname(args.exp_dirs[0])
            dir_name = os.path.basename(args.exp_dirs[0])
            args.eval_dir = os.path.join(parent_dir, dir_name + '-eval')
            logging.info('Eval dir: "%s"' % args.eval_dir)
        
        return args
        
    

class Evaluation(object):
    '''
    Base class for all evaluations
    '''
    
    def __init__(self, parser=EvalOptionParser()):
        self.parser = parser
        args = self.parser.parse_args()
        # Give all the options to the experiment instance
        self.__dict__.update(args.__dict__)
        
    def evaluate(self):
        raise Exception('Not Implemented')
        
    def _get_run_dirs(self):
        run_dirs = []
        for dir in self.exp_dirs:
            run_dirs.extend(glob(os.path.join(dir, 'runs-*-*', '*')))
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
    def __init__(self, name, regex_string, group, file, required, type, flags):
        self.name = name
        self.group = group
        self.file = file
        self.required = required
        self.type = type
        
        flag = 0
        
        for char in flags:
            if   char == 'M': flag |= re.M
            elif char == 'L': flag |= re.L
            elif char == 'S': flag |= re.S
            elif char == 'I': flag |= re.I
            elif char == 'U': flag |= re.U
            elif char == 'X': flag |= re.X
        
        self.regex = re.compile(regex_string, flag)
        
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
        
        
    def add_pattern(self, name, regex_string, group=1, file='run.log', required=True,
                        type=str, flags=''):
        '''
        During evaluate() look for pattern in file and add what is found in group
        to the properties dictionary under "name"
        
        properties[name] = re.compile(regex_string).search(file_content).group(group)
        
        If required is True and the pattern is not found in file, an error
        message is printed
        '''
        #defaults = {'group': 1, 'file': 'run.log', 'required': True,
        #            'type': str, 'flags': ''}
        #defaults.update(kwargs)
        pattern = Pattern(name, regex_string, group, file, required, type, flags)
        self.patterns[pattern.file].append(pattern)
        
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
                    value = pattern.type(value)
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
    eval.add_key_value_pattern('run_start_time')
    eval.add_pattern('initial_h_value', r'Initial state h value: (\d+)', type=int, required=False)
    eval.add_pattern('plan_length', r'Plan length: (\d+)', type=int)
    eval.add_pattern('expanded', r'Expanded (\d+)', type=int)
    eval.add_pattern('generated', r'Generated (\d+)', type=int)
    eval.add_pattern('search_time', r'Search time: (.+)s', type=float)
    eval.add_pattern('total_time', r'Total time: (.+)s', type=float)
    
    eval.add_pattern('translator_vars', r'begin_variables\n(\d+)', file='output.sas', type=int, flags='M')
    eval.add_pattern('translator_ops', r'end_goal\n(\d+)', file='output.sas', type=int, flags='M')
    
    eval.add_pattern('preprocessor_vars', r'begin_variables\n(\d+)', file='output', type=int, flags='M')
    eval.add_pattern('preprocessor_ops', r'end_goal\n(\d+)', file='output', type=int, flags='M')
    
    def completely_explored(content, old_props):
        new_props = {}
        if 'Completely explored state space -- no solution!' in content:
            new_props['completely_explored'] = True
        return new_props
    
    def get_status(content, old_props):
        new_props = {}
        if 'does not support' in content:
            new_props['status'] = 'unsupported'
        elif 'plan_length' in old_props:
            new_props['status'] = 'ok'
        elif 'completely_explored' in old_props:
            new_props['status'] = 'failure'
        else:
            new_props['status'] = 'not_ok'
        return new_props
        
    def solved(content, old_props):
        new_props = {}
        if 'plan_length' in old_props:
            new_props['solved'] = 1
        else:
            new_props['solved'] = 0
        return new_props
        
        
    def get_total_values(content):
        vars_regex = re.compile(r'begin_variables\n\d+\n(.+)end_variables', re.M|re.S)
        match = vars_regex.search(content)
        if not match:
            logging.error('Total number of values could not be found')
            return {}
        """
        var_descriptions looks like
        ['var0 7 -1', 'var1 4 -1', 'var2 4 -1', 'var3 3 -1']
        """
        var_descriptions = match.group(1).splitlines()
        #print 'VARS', var_descriptions
        total_domain_size = 0
        for var in var_descriptions:
            var_name, domain_size, init_value = var.split()
            #assert len(parts) == 3
            #domain_size = parts[1]
            total_domain_size += int(domain_size)
        return total_domain_size
        
    def translator_total_values(content, old_props):
        return {'translator_total_values': get_total_values(content)}
        
    def preprocessor_total_values(content, old_props):
        return {'preprocessor_total_values': get_total_values(content)}
        
        
    def get_axioms(content):
        """
        If |axioms| > 0:  ...end_operator\nAXIOMS\nbegin_rule...
        If |axioms| == 0: ...end_operator\n0
        """
        regex = re.compile(r'end_operator\n(\d+)\nbegin_rule', re.M|re.S)
        match = regex.search(content)
        if not match:
            # make sure we have a valid file here
            regex = re.compile(r'end_operator\n(\d+)', re.M|re.S)
            match = regex.search(content)
            assert match.group(1) == '0'
        axioms = int(match.group(1))
        return axioms
        
    def translator_axioms(content, old_props):
        return {'translator_axioms': get_axioms(content)}
        
    def preprocessor_axioms(content, old_props):
        return {'preprocessor_axioms': get_axioms(content)}
        
        
    def cg_arcs(content, old_props):
        """
        Sums up the number of outgoing arcs for each vertex
        """
        regex = re.compile(r'begin_CG\n(.+)end_CG', re.M|re.S)
        match = regex.search(content)
        if not match:
            logging.error('Number of arcs could not be determined')
            return {}
        """
        cg looks like
        ['6', '1 16', '2 16', '3 8', '4 8', '5 8', '6 8', '4', ...]
        """
        cg = match.group(1).splitlines()
        print cg
        arcs = 0
        for line in cg:
            parts = line.split()
            parts = map(lambda part: part.strip(), parts)
            parts = filter(lambda part: len(part) > 0, parts)
            if len(parts) == 1:
                # We have a line containing the number of arcs for one node
                arcs += int(parts[0])
        return {'cg_arcs': arcs}
        
        
    eval.add_function(completely_explored)
    eval.add_function(get_status)
    eval.add_function(solved)
    
    eval.add_function(translator_total_values, file='output.sas')
    eval.add_function(preprocessor_total_values, file='output')
    
    eval.add_function(translator_axioms, file='output.sas')
    eval.add_function(preprocessor_axioms, file='output')
    
    eval.add_function(cg_arcs, file='output')
    
    return eval


if __name__ == "__main__":
    #if len(sys.argv) == 1:
    #    print 'Testing'
    #    sys.argv.extend('-s test'.split())
        
    eval = build_evaluator()
    eval.evaluate()
    
