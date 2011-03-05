#! /usr/bin/env python
"""
Module that permits copying and parsing experiment files

If called as the main script, it will only copy the files and do no parsing
By default only one properties file is written. With the "--copy-all" parameter
all files will be copied.
"""

from __future__ import with_statement

import os
import sys
import re
from glob import glob
from collections import defaultdict
import logging

import tools


class FetchOptionParser(tools.ArgParser):
    def __init__(self, *args, **kwargs):
        tools.ArgParser.__init__(self, *args, **kwargs)

        self.add_argument('exp_dir',
                help='path to experiment directory', type=self.directory)

        self.add_argument('-d', '--dest', dest='eval_dir', default='',
                help='path to evaluation directory (default: <exp_dir>-eval)')

        self.add_argument('--copy-all', action='store_true',
                help='copy all files from run dirs to new directory tree, '
                    'not only the properties files')

    def parse_args(self, *args, **kwargs):
        # args is the populated namespace, i.e. the Fetcher instance
        args = tools.ArgParser.parse_args(self, *args, **kwargs)

        args.exp_dir = os.path.abspath(args.exp_dir)
        logging.info('Exp dir:  "%s"' % args.exp_dir)

        if args.exp_dir.endswith('eval'):
            msg = ('The source directory seems to be an evaluation directory. '
                   'Are you sure you this is an experiment directory? (Y/N): ')
            answer = raw_input(msg)
            if not answer.upper() == 'Y':
                sys.exit()

        # Update some args with the values from the experiment's
        # properties file if the values have not been set on the commandline
        exp_props_file = os.path.join(args.exp_dir, 'properties')
        if os.path.exists(exp_props_file):
            exp_props = tools.Properties(exp_props_file)
            if not args.eval_dir and 'eval_dir' in exp_props:
                args.eval_dir = exp_props['eval_dir']
            if 'copy_all' in exp_props:
                args.copy_all = exp_props['copy_all']

        # If args.eval_dir is absolute already we don't have to do anything
        if args.eval_dir and not os.path.isabs(args.eval_dir):
            args.eval_dir = os.path.abspath(args.eval_dir)
        elif not args.eval_dir:
            args.eval_dir = args.eval_dir or args.exp_dir + '-eval'

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
                    msg = 'Atrribute %s not found for pattern %s in file %s'
                    msg %= (attribute_name, self, filename)
                    logging.error(msg)
        elif self.required:
            logging.error('Pattern %s not found in %s' % (self, filename))
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

    def parse(self, orig_props):
        assert self.filename
        orig_props.update(self._search_patterns())
        orig_props.update(self._apply_functions(orig_props))
        return orig_props

    def _search_patterns(self):
        found_props = {}
        reversed_content = '\n'.join(reversed(self.content.splitlines()))

        for pattern in self.patterns:
            found_props.update(pattern.search(reversed_content, self.filename))
        return found_props

    def _apply_functions(self, props):
        for function in self.functions:
            props.update(function(self.content, props))
        return props


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
        self.check = None

    def _get_run_dirs(self):
        return sorted(glob(os.path.join(self.exp_dir, 'runs-*-*', '*')))

    def add_pattern(self, name, regex_string, group=1, file='run.log',
                        required=True, type=int, flags=''):
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

    def set_check(self, function):
        """
        After all properties have been parsed or calculated, run "function"
        on them to assert some things.
        """
        self.check = function

    def fetch(self):
        total_dirs = len(self.run_dirs)

        combined_props_filename = os.path.join(self.eval_dir, 'properties')
        combined_props = tools.Properties(combined_props_filename)

        for index, run_dir in enumerate(self.run_dirs, 1):
            prop_file = os.path.join(run_dir, 'properties')
            props = tools.Properties(prop_file)

            id = props.get('id')
            dest_dir = os.path.join(self.eval_dir, *id)
            if self.copy_all:
                tools.makedirs(dest_dir)
                tools.fast_updatetree(run_dir, dest_dir)

            props['run_dir'] = os.path.relpath(run_dir, self.exp_dir)

            for filename, file_parser in self.file_parsers.items():
                filename = os.path.join(run_dir, filename)
                file_parser.load_file(filename)
                props = file_parser.parse(props)

            combined_props['-'.join(id)] = props.dict()
            if self.copy_all:
                # Write new properties file
                props.filename = os.path.join(dest_dir, 'properties')
                props.write()

            if self.check:
                try:
                    self.check(props)
                except AssertionError, e:
                    msg = 'Parsed properties not valid in %s: %s'
                    logging.error(msg % (prop_file, e))
                    print '*' * 60
                    props.write(sys.stdout)
                    print '*' * 60
            logging.info('Done Evaluating: %6d/%d' % (index, total_dirs))

        tools.makedirs(self.eval_dir)
        combined_props.write()


if __name__ == "__main__":
    logging.info('Import this module if you want to parse the output files')
    logging.info('Started copying files')
    fetcher = Fetcher()
    fetcher.fetch()
    logging.info('Finished copying files')
