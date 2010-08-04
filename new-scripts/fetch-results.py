#! /usr/bin/env python
"""
Module that permits evaluating experiments conducted with experiments.py
"""

from __future__ import with_statement

import os
import sys
import shutil
import re
from glob import glob
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(levelname)-8s %(message)s',)
                    
import tools
from external import argparse
      

class EvalOptionParser(tools.ArgParser):
    def __init__(self, *args, **kwargs):
        tools.ArgParser.__init__(self, *args, **kwargs)
      
        self.add_argument('exp_dirs', nargs='+',
                help='path to experiment directory', type=self.directory)
        
        self.add_argument('-d', '--dest', dest='eval_dir', default='',
                help='path to evaluation directory (default: <exp_dirs>-eval)')
            
    
    def parse_args(self, *args, **kwargs):
        # args is the populated namespace, i.e. the evaluation instance
        args = argparse.ArgumentParser.parse_args(self, *args, **kwargs)
        
        args.exp_dirs = map(lambda dir: os.path.normpath(os.path.abspath(dir)), args.exp_dirs)
        logging.info('Exp dirs: "%s"' % args.exp_dirs)
        
        if not args.eval_dir:
            parent_dir = os.path.dirname(args.exp_dirs[0])
            dir_name = os.path.basename(args.exp_dirs[0])
            args.eval_dir = os.path.join(parent_dir, dir_name + '-eval')
            logging.info('Eval dir: "%s"' % args.eval_dir)
        
        return args
        
    

class Evaluation(object):
    """
    Base class for all evaluations
    """
    def __init__(self, parser=EvalOptionParser()):
        self.parser = parser
        # Give all the options to the experiment instance
        self.parser.parse_args(namespace=self)
        
        self.run_dirs = self._get_run_dirs()
        
    def evaluate(self):
        raise Exception('Not Implemented')
        
    def _get_run_dirs(self):
        run_dirs = []
        for dir in self.exp_dirs:
            run_dirs.extend(glob(os.path.join(dir, 'runs-*-*', '*')))
        return run_dirs
        
        
        
class CopyEvaluation(Evaluation):
    """
    Evaluation that copies files from run dirs into a new tree under
    <eval-dir> according to the value "id" in the run's properties file
    """
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
        
        total_dirs = len(copy_dict.items())
            
        for index, (source, dest) in enumerate(copy_dict.items(), 1):
            logging.info('Done copying: %d/%d' % (index, total_dirs))
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
        
        

class ParseEvaluation(Evaluation):
    """
    Evaluation that parses various files and writes found results
    into the run's properties file
    """
    def __init__(self, *args, **kwargs):
        Evaluation.__init__(self, *args, **kwargs)
        
        self.patterns = defaultdict(list)
        self.functions = defaultdict(list)
        
        
    def add_pattern(self, name, regex_string, group=1, file='run.log', required=True,
                        type=str, flags=''):
        """
        During evaluate() look for pattern in file and add what is found in group
        to the properties dictionary under "name"
        
        properties[name] = re.compile(regex_string).search(file_content).group(group)
        
        If required is True and the pattern is not found in file, an error
        message is printed
        """
        pattern = Pattern(name, regex_string, group, file, required, type, flags)
        self.patterns[pattern.file].append(pattern)
        
    def add_key_value_pattern(self, name, file='run.log'):
        """
        Convenience method that adds a pattern for lines containing only a
        key:value pair
        """
        regex_string = r'\s*%s\s*[:=]\s*(.+)' % name
        self.add_pattern(name, regex_string, 1, file)
        
        
    def add_function(self, function, file='run.log'):
        """
        After all the patterns have been evaluated and the found values have
        been inserted into the properties files, call function(file_content, props)
        for each added function.
        The function is supposed to return a dictionary with new properties.
        """
        self.functions[file].append(function)
        
        
    def evaluate(self):
        #CopyEvaluation.evaluate(self)
        
        total_dirs = len(self.run_dirs)
        
        for index, run_dir in enumerate(self.run_dirs, 1):
            
            copy_files = {}
            
            
            prop_file = os.path.join(run_dir, 'properties')
            props = tools.Properties(prop_file)
            props['run_dir'] = run_dir
            
            for file, patterns in self.patterns.items():
                file = os.path.join(run_dir, file)
                new_props = self._parse_file(file, patterns)
                props.update(new_props)
            for file, functions in self.functions.items():
                file = os.path.join(run_dir, file)
                new_props = self._apply_functions(file, functions, props)
                props.update(new_props)
            
            # Write new properties file
            id = props.get('id')
            dest_dir = os.path.join(self.eval_dir, *id)
            tools.makedirs(dest_dir)
            props.filename = os.path.join(dest_dir, 'properties')
            props.write()
            
            logging.info('Done Parsing: %6d/%d' % (index, total_dirs))
            
            
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
    #eval.add_key_value_pattern('run_start_time')
    eval.add_pattern('initial_h_value', r'Initial state h value: (\d+)', type=int, required=False)
    eval.add_pattern('plan_length', r'Plan length: (\d+)', type=int, required=False)
    eval.add_pattern('expanded', r'Expanded (\d+)', type=int, required=False)
    eval.add_pattern('generated', r'Generated (\d+)', type=int)
    eval.add_pattern('search_time', r'Search time: (.+)s', type=float, required=False)
    eval.add_pattern('total_time', r'Total time: (.+)s', type=float, required=False)
    
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
        total_domain_size = 0
        for var in var_descriptions:
            var_name, domain_size, axiom_layer = var.split()
            total_domain_size += int(domain_size)
        return total_domain_size
        
    def translator_total_values(content, old_props):
        return {'translator_total_values': get_total_values(content)}
        
    def preprocessor_total_values(content, old_props):
        return {'preprocessor_total_values': get_total_values(content)}
        
        
    def get_derived_vars(content):
        """
        Count those variables that have an axiom_layer >= 0
        """
        regex = re.compile(r'begin_variables\n\d+\n(.+)end_variables', re.M|re.S)
        match = regex.search(content)
        if not match:
            logging.error('Number of derived vars could not be found')
            return {}
        """
        var_descriptions looks like
        ['var0 7 -1', 'var1 4 -1', 'var2 4 -1', 'var3 3 -1']
        """
        var_descriptions = match.group(1).splitlines()
        derived_vars = 0
        for var in var_descriptions:
            var_name, domain_size, axiom_layer = var.split()
            if int(axiom_layer) >= 0:
                derived_vars += 1
        return derived_vars
        
    def translator_derived_vars(content, old_props):
        return {'translator_derived_vars': get_derived_vars(content)}
        
    def preprocessor_derived_vars(content, old_props):
        return {'preprocessor_derived_vars': get_derived_vars(content)}
        
        
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
            
            if match is None:
                # Some mystery problems don't have any operators
                assert 'begin_rule' not in content, content
                return 0
            else:
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
    
    eval.add_function(translator_derived_vars, file='output.sas')
    eval.add_function(preprocessor_derived_vars, file='output')
    
    eval.add_function(cg_arcs, file='output')
    
    return eval


if __name__ == '__main__':
    #if len(sys.argv) == 1:
    #    print 'Testing'
    #    sys.argv.extend('-s test'.split())
        
    eval = build_evaluator()
    eval.evaluate()
    
