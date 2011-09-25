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
import hashlib
import cPickle

import tools


class FetchOptionParser(tools.ArgParser):
    def __init__(self, *args, **kwargs):
        tools.ArgParser.__init__(self, *args, **kwargs)

        self.add_argument('exp_dir',
                help='Path to experiment directory', type=self.directory)

        self.add_argument('-d', '--dest', dest='eval_dir', default='',
                help='Path to evaluation directory (default: <exp_dir>-eval)')

        self.add_argument('--copy-all', action='store_true',
                help='Copy all files from run dirs to a new directory tree. '
                     'Without this option only the combined properties file '
                     'is written do disk.')

        self.add_argument('--no-props-file', action='store_true',
                help='Do not write the combined properties file.')

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
        args.exp_props = tools.Properties(exp_props_file)
        if not args.eval_dir and 'eval_dir' in args.exp_props:
            args.eval_dir = args.exp_props['eval_dir']
        if 'copy_all' in args.exp_props:
            args.copy_all = args.exp_props['copy_all']
        if 'no_props_file' in args.exp_props:
            args.no_props_file = args.exp_props['no_props_file']

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
    Each group_number has an associated attribute name and a type.
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


class _FileParser(object):
    """
    Private class that parses a given file according to the added patterns
    and functions.
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
            self.content = ''
            return False
        else:
            return True

    def add_pattern(self, pattern):
        self.patterns.append(pattern)

    def add_function(self, function):
        self.functions.append(function)

    def parse(self, props):
        assert self.filename
        props.update(self._search_patterns())
        self._apply_functions(props)

    def _search_patterns(self):
        found_props = {}
        for pattern in self.patterns:
            found_props.update(pattern.search(self.content, self.filename))
        return found_props

    def _apply_functions(self, props):
        for function in self.functions:
            function(self.content, props)


class Fetcher(object):
    """
    If copy-all is True, copies files from run dirs into a new tree under
    <eval-dir> according to the value "id" in the run's properties file.

    Parses files and writes found results into the run's properties file or
    into a global properties file.
    """
    def __init__(self, parser=FetchOptionParser(), *args, **kwargs):
        # Give all the options to the experiment instance
        parser.parse_args(namespace=self)

        self.file_parsers = defaultdict(_FileParser)
        self.check = None
        self.postprocess_functions = []

    def add_pattern(self, name, regex, group=1, file='run.log', required=True,
                    type=int, flags=''):
        """
        During evaluate() look for pattern in file and add what is found in
        group to the properties dictionary under "name":

        properties[name] = re.compile(regex).search(file_content).group(group)

        If required is True and the pattern is not found in file, an error
        message is printed
        """
        groups = [(group, name, type)]
        self.add_multipattern(groups, regex, file, required, flags)

    def add_multipattern(self, groups, regex, file='run.log', required=True,
                         flags=''):
        """
        During evaluate() look for "regex" in file. For each tuple of
        (group_number, attribute_name, type) add the results for "group_number"
        to the properties file under "attribute_name" after casting it to
        "type".

        If required is True and the pattern is not found in file, an error
        message is printed
        """
        self.file_parsers[file].add_pattern(
                        _MultiPattern(groups, regex, file, required, flags))

    def add_function(self, function, file='run.log'):
        """
        After all the patterns have been evaluated and the found values have
        been inserted into the properties files, call
        function(file_content, props) for each added function.
        The function can directly manipulate the properties dictionary "props".
        Functions can use the fact that all patterns have been parsed before
        any function is run on the file content. The found values are present
        in "props".
        """
        self.file_parsers[file].add_function(function)

    def set_check(self, function):
        """
        After all properties have been parsed or calculated, run "function"
        on them to assert some things.
        """
        self.check = function

    def apply_postprocess_functions(self, combined_props):
        if not self.postprocess_functions:
            return

        prob_to_runs = defaultdict(list)
        for run_name, run in combined_props.items():
            prob = '%s:%s' % (run['domain'], run['problem'])
            prob_to_runs[prob].append(run)

        for func in self.postprocess_functions:
            for prob, problem_runs in prob_to_runs.items():
                func(problem_runs)

    def fetch_dir(self, run_dir):
        prop_file = os.path.join(run_dir, 'properties')
        props = tools.Properties(prop_file)

        id = props.get('id')
        # Abort if an id cannot be read.
        if not id:
            logging.error('id is not set in %s.' % prop_file)
            sys.exit(1)

        dest_dir = os.path.join(self.eval_dir, *id)
        if self.copy_all:
            tools.makedirs(dest_dir)
            tools.fast_updatetree(run_dir, dest_dir)

        props['run_dir'] = os.path.relpath(run_dir, self.exp_dir)

        for filename, file_parser in self.file_parsers.items():
            # If filename is absolute it will not be changed here
            path = os.path.join(run_dir, filename)
            success = file_parser.load_file(path)
            if success:
                # Subclasses directly modify the properties during parsing
                file_parser.parse(props)
            else:
                logging.error('File "%s" could not be read' % path)

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
        return '-'.join(id), props

    def fetch(self):
        total_dirs = self.exp_props.get('runs')

        if not self.no_props_file:
            combined_props_filename = os.path.join(self.eval_dir, 'properties')
            combined_props = tools.Properties(combined_props_filename)

        # Get all run_dirs
        run_dirs = sorted(glob(os.path.join(self.exp_dir, 'runs-*-*', '*')))
        for index, run_dir in enumerate(run_dirs, 1):
            logging.info('Evaluating: %6d/%d' % (index, total_dirs))
            id_string, props = self.fetch_dir(run_dir)
            if not self.no_props_file:
                props['id-string'] = id_string
                combined_props[id_string] = props.dict()

        tools.makedirs(self.eval_dir)
        if not self.no_props_file:
            self.apply_postprocess_functions(combined_props)
            combined_props.write()
            self.write_data_dump(combined_props)

    def write_data_dump(self, combined_props):
        combined_props_file = combined_props.filename
        dump_path = os.path.join(self.eval_dir, 'data_dump')
        logging.info('Reading properties file without parsing')
        properties_contents = open(combined_props_file).read()
        logging.info('Calculating properties hash')
        new_checksum = hashlib.md5(properties_contents).digest()
        data = combined_props.get_dataset()
        logging.info('Finished turning properties into dataset')
        # Pickle data for faster future use
        cPickle.dump((new_checksum, data), open(dump_path, 'wb'),
                     cPickle.HIGHEST_PROTOCOL)
        logging.info('Wrote data dump')


if __name__ == "__main__":
    logging.info('Import this module if you want to parse the output files')
    with tools.timing('Copy files'):
        fetcher = Fetcher()
        fetcher.fetch()
