#! /usr/bin/env python
"""
Module that permits copying and parsing experiment files
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
      

class EvalOptionParser(tools.ArgParser):
    def __init__(self, *args, **kwargs):
        tools.ArgParser.__init__(self, *args, **kwargs)
      
        self.add_argument('exp_dirs', nargs='+',
                help='path to experiment directory', type=self.directory)
        
        self.add_argument('-d', '--dest', dest='eval_dir', default='',
                help='path to evaluation directory (default: <exp_dirs>-eval)')
                
        self.add_argument('-c', '--copy-all', default=False, action='store_true', 
                help='copy all files from run dirs to new directory tree, '
                    'not only the properties files')
            
    
    def parse_args(self, *args, **kwargs):
        # args is the populated namespace, i.e. the evaluation instance
        args = tools.ArgParser.parse_args(self, *args, **kwargs)
        
        args.exp_dirs = map(lambda dir: os.path.normpath(os.path.abspath(dir)), args.exp_dirs)
        logging.info('Exp dirs: "%s"' % args.exp_dirs)
        
        if not args.eval_dir:
            parent_dir = os.path.dirname(args.exp_dirs[0])
            dir_name = os.path.basename(args.exp_dirs[0])
            args.eval_dir = os.path.join(parent_dir, dir_name + '-eval')
            logging.info('Eval dir: "%s"' % args.eval_dir)
        
        return args
        
        
    
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
        
        

class Evaluation(object):
    """
    If copy-all is True, copies files from run dirs into a new tree under
    <eval-dir> according to the value "id" in the run's properties file
    
    Parses various files and writes found results
    into the run's properties file
    """
    def __init__(self, parser=EvalOptionParser(), *args, **kwargs):
        self.parser = parser
        # Give all the options to the experiment instance
        self.parser.parse_args(namespace=self)
        
        self.run_dirs = self._get_run_dirs()
        
        self.patterns = defaultdict(list)
        self.functions = defaultdict(list)
    
        
    def _get_run_dirs(self):
        run_dirs = []
        for dir in self.exp_dirs:
            run_dirs.extend(glob(os.path.join(dir, 'runs-*-*', '*')))
        return run_dirs        
        
        
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
        total_dirs = len(self.run_dirs)
        
        for index, run_dir in enumerate(self.run_dirs, 1):
            prop_file = os.path.join(run_dir, 'properties')
            props = tools.Properties(prop_file)
            
            id = props.get('id')
            dest_dir = os.path.join(self.eval_dir, *id)
            if self.copy_all:
                tools.fast_updatetree(run_dir, dest_dir)
            
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
            #id = props.get('id')
            #dest_dir = os.path.join(self.eval_dir, *id)
            #tools.makedirs(dest_dir)
            props.filename = os.path.join(dest_dir, 'properties')
            props.write()
            
            logging.info('Done Evaluating: %6d/%d' % (index, total_dirs))
            
            
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
        
        
if __name__ == "__main__":
    logging.error('Please import this module from another script')

    
