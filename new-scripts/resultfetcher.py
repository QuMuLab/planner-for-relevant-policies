#! /usr/bin/env python
"""
Module that permits copying and parsing experiment files

If called as the main script, it will only copy the files and do no parsing
By default only the properties files are copied, with the "-c" parameter all 
files will be copied.

Some timings (issue7-ou-lmcut):
Copy-props No-regexes   No-functions   42s
Copy-all   No-regexes   No-functions   17min
Copy-props Regexes      Functions      67min
Copy-props Regexes      No-Functions   7min
Copy-props More-Regexes Less-Functions 9min
"""

from __future__ import with_statement

import os
import sys
import shutil
import re
from glob import glob
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)-s %(levelname)-8s %(message)s',)
                    
import tools
      

class FetchOptionParser(tools.ArgParser):
    def __init__(self, *args, **kwargs):
        tools.ArgParser.__init__(self, *args, **kwargs)
      
        self.add_argument('exp_dir',
                help='path to experiment directory', type=self.directory)
        
        self.add_argument('-d', '--dest', dest='eval_dir', default='',
                help='path to evaluation directory (default: <exp_dir>-eval)')
                
        self.add_argument('-c', '--copy-all', default=False, action='store_true', 
                help='copy all files from run dirs to new directory tree, '
                    'not only the properties files')
            
    
    def parse_args(self, *args, **kwargs):
        # args is the populated namespace, i.e. the Fetcher instance
        args = tools.ArgParser.parse_args(self, *args, **kwargs)
        
        args.exp_dir = os.path.normpath(os.path.abspath(args.exp_dir))
        logging.info('Exp dir: "%s"' % args.exp_dir)
        
        if args.exp_dir.endswith('eval'):
            answer = raw_input('The source directory seems to be an evaluation '
                                'directory. Are you sure you this is an '
                                'experiment directory? (Y/N): ')
            if not answer.upper() == 'Y':
                sys.exit()
        
        # Update some args with the values from the experiment's properties file
        # if the values have not been set on the commandline
        exp_props_file = os.path.join(args.exp_dir, 'properties')
        if os.path.exists(exp_props_file):
            exp_props = tools.Properties(exp_props_file)
            if not args.eval_dir and 'eval_dir' in exp_props:
                args.eval_dir = exp_props['eval_dir']
            if 'copy_all' in exp_props:
                args.copy_all = exp_props['copy_all']
            #args.__dict__.update(exp_props)
            #args.eval_dir = exp_props.get('eval_dir', None)
        
        if not args.eval_dir or not os.path.isabs(args.eval_dir):
            dir_name = os.path.basename(args.exp_dir)
            name = args.eval_dir or dir_name + '-eval'
            parent_dir = os.path.dirname(args.exp_dir)
            args.eval_dir = os.path.join(parent_dir, name)
        
        logging.info('Eval dir: "%s"' % args.eval_dir)
        
        return args
        

class _MultiPattern(object):
    """
    Parses a file for a pattern containing multiple match groups.
    Each group_number has an associated attribute name and a type
    """
    def __init__(self, groups, regex, file, required, flags):
        """
        groups is a list of (group_number, attribute_name, type) tuples
        """
        self.groups = groups
        self.file = file
        self.required = required
        
        flag = 0
        
        for char in flags:
            if   char == 'M': flag |= re.M
            elif char == 'L': flag |= re.L
            elif char == 'S': flag |= re.S
            elif char == 'I': flag |= re.I
            elif char == 'U': flag |= re.U
            elif char == 'X': flag |= re.X
        
        self.regex = re.compile(regex, flag)
        
    def search(self, content, filename):
        found_props = {}
        match = self.regex.search(content)
        if match:
            for group_number, attribute_name, type in self.groups:
                try:
                    value = match.group(group_number)
                    value = type(value)
                    found_props[attribute_name] = value
                except IndexError:
                    msg = 'Atrribute "%s" not found for pattern "%s" in file "%s"'
                    msg %= (attribute_name, self, filename)
                    logging.error(msg)
        elif pattern.required:
            logging.error('_Pattern "%s" not present in file "%s"' % \
                                                (self, filename))
        return found_props
        
    def __str__(self):
        return self.regex.pattern
    

class _Pattern(_MultiPattern):
    def __init__(self, name, regex, group, file, required, type, flags):
        groups = [(group, name, type)]
        _MultiPattern.__init__(self, groups, regex, file, required, flags)
        
        
        
class _FileParser(object):
    """
    Private class that parses a given file according to the added patterns
    and functions
    """
    def __init__(self):
        self.filename = None
        self.content = None
        
        self.patterns = []
        self.functions = []
        
    def load_file(self, filename):
        self.filename = filename
       
        try:
            with open(filename, 'rb') as file:
                self.content = file.read()
        except IOError, err:
            logging.error('File "%s" could not be read (%s)' % (filename, err))
            self.content = ''
        
    def add_pattern(self, pattern):
        self.patterns.append(pattern)
        
    def add_function(self, function):
        self.functions.append(function)
        
    def parse(self):
        assert self.filename
        props = {}
        for pattern in self.patterns:
            props.update(self._search_patterns())
        for function in self.functions:
            props.update(self._apply_functions(props))
        return props
    
    
    def _search_patterns(self):
        found_props = {}
        
        for pattern in self.patterns:
            found_props.update(pattern.search(self.content, self.filename))
        return found_props
        
        
    def _apply_functions(self, old_props):
        new_props = {}
        
        for function in self.functions:
            new_props.update(function(self.content, old_props))
        return new_props
    
        
    
        

class Fetcher(object):
    """
    If copy-all is True, copies files from run dirs into a new tree under
    <eval-dir> according to the value "id" in the run's properties file
    
    Parses various files and writes found results
    into the run's properties file
    """
    def __init__(self, parser=FetchOptionParser(), *args, **kwargs):
        # Give all the options to the experiment instance
        parser.parse_args(namespace=self)
        
        self.run_dirs = self._get_run_dirs()
        
        self.file_parsers = defaultdict(_FileParser)
        
    def _get_run_dirs(self):
        return glob(os.path.join(self.exp_dir, 'runs-*-*', '*'))
        
    def add_pattern(self, name, regex_string, group=1, file='run.log', 
                        required=True, type=str, flags=''):
        """
        During evaluate() look for pattern in file and add what is found in 
        group to the properties dictionary under "name"
        
        properties[name] = re.compile(regex_str).search(file_content).group(group)
        
        If required is True and the pattern is not found in file, an error
        message is printed
        """
        pattern = _Pattern(name, regex_string, group, file, required, type, flags)
        self.file_parsers[file].add_pattern(pattern)
        
    def add_multipattern(self, groups, regex, file='run.log', required=True, flags=''):
        """
        During evaluate() look for "regex" in file. For each tuple of
        (group_number, attribute_name, type) add the results for "group_number" 
        to the properties file under "attribute_name" after casting it to "type".
        
        If required is True and the pattern is not found in file, an error
        message is printed
        """
        pattern = _MultiPattern(groups, regex, file, required, flags)
        self.file_parsers[file].add_pattern(pattern)
        
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
        self.file_parsers[file].add_function(function)
        
    def fetch(self):
        total_dirs = len(self.run_dirs)
        
        for index, run_dir in enumerate(self.run_dirs, 1):
            prop_file = os.path.join(run_dir, 'properties')
            props = tools.Properties(prop_file)
            
            id = props.get('id')
            dest_dir = os.path.join(self.eval_dir, *id)
            tools.makedirs(dest_dir)
            if self.copy_all:
                tools.fast_updatetree(run_dir, dest_dir)
            
            props['run_dir'] = run_dir
            
            for filename, file_parser in self.file_parsers.items():
                filename = os.path.join(run_dir, filename)
                file_parser.load_file(filename)
                props.update(file_parser.parse())
            
            # Write new properties file
            props.filename = os.path.join(dest_dir, 'properties')
            props.write()
            
            logging.info('Done Evaluating: %6d/%d' % (index, total_dirs))
            
    
        
        
if __name__ == "__main__":
    logging.info('Import this module if you want to parse the output files')
    logging.info('Started copying files')
    fetcher = Fetcher()
    fetcher.fetch()
    logging.info('Finished copying files')

    
