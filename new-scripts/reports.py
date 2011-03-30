#! /usr/bin/env python
"""
Module that permits generating reports by reading properties files
"""

from __future__ import with_statement, division

import os
import sys
from itertools import combinations
import logging
import collections
import cPickle
import hashlib

import tools
from markup import Document
from external.datasets import DataSet
from external import txt2tags


def avg(values):
    """Computes the arithmetic mean of a list of numbers.

    >>> print avg([20, 30, 70])
    40.0
    """
    return round(sum(values, 0.0) / len(values), 4)


def gm(values):
    """Computes the geometric mean of a list of numbers.

    >>> print gm([2, 8])
    4.0
    """
    assert len(values) >= 1
    exp = 1.0 / len(values)
    return round(tools.prod([val ** exp for val in values]), 4)


class ReportArgParser(tools.ArgParser):
    def __init__(self, *args, **kwargs):
        tools.ArgParser.__init__(self, *args, add_help=True, **kwargs)

        self.add_argument('source', help='path to results directory',
                    type=self.directory)

        self.add_argument('-d', '--dest', dest='report_dir', default='reports',
                    help='path to report directory')

        self.add_argument('--format', dest='output_format', default='html',
                    help='format of the output file',
                    choices=sorted(txt2tags.TARGETS))

        self.add_argument('--group-func', default='sum',
                    help='the function used to cumulate the values of a group')

        self.add_argument('--hide-sum', dest='hide_sum_row',
                    default=False, action='store_true',
                    help='do not add a row that sums up each column')

        self.add_argument('--dry', default=False, action='store_true',
                    help='do not write anything to the filesystem')

        self.add_argument('--show_attributes', action='store_true',
                    help='show a list of available attributes and exit')

        self.add_argument('--open', default=False, action='store_true',
                    dest='open_report',
                    help='open the report file after writing it')

        self.add_argument('-a', '--attributes', dest='foci', type=tools.csv,
                    metavar='ATTR',
                    help='the analyzed attributes (e.g. "expanded"). '
                    'If omitted, use all found numerical attributes')

    def parse_args(self, *args, **kwargs):
        args = tools.ArgParser.parse_args(self, *args, **kwargs)

        args.eval_dir = args.source

        args.eval_dir = os.path.normpath(os.path.abspath(args.eval_dir))
        logging.info('Eval dir: "%s"' % args.eval_dir)

        if not args.eval_dir.endswith('eval'):
            msg = ('The source directory does not end with eval. '
                   'Are you sure you this is an evaluation directory? (Y/N): ')
            answer = raw_input(msg)
            if not answer.upper() == 'Y':
                sys.exit()

        if not os.path.exists(args.report_dir):
            os.makedirs(args.report_dir)

        # Turn e.g. the string 'max' into the function max()
        args.group_func = eval(args.group_func)

        return args


class Report(object):
    """
    Base class for all reports
    """
    def __init__(self, parser=ReportArgParser()):
        # Give all the options to the report instance
        parser.parse_args(namespace=self)

        self.data = None
        self.orig_data = self._get_data()
        self.data = self.orig_data.copy()

        attributes = sorted(self.orig_data.get_attributes())

        if self.show_attributes:
            print '\nAvailable attributes: %s' % attributes
            sys.exit()

        if not self.foci or self.foci == 'all':
            self.foci = attributes
        self.foci.sort()
        logging.info('Attributes: %s' % self.foci)

        self.filter_funcs = []
        self.filter_pairs = {}

        self.grouping = []
        self.order = []

        self.infos = []

    def add_filter(self, *filter_funcs, **filter_pairs):
        self.filter_funcs.extend(filter_funcs)
        self.filter_pairs.update(filter_pairs)

    def set_grouping(self, *grouping):
        """
        Set by which attributes the runs should be separated into groups

        grouping = None/[]: Use only one big group (default)
        grouping = 'domain': group by domain
        grouping = ['domain', 'problem']: Use one group for each problem
        """
        self.grouping = grouping

    def set_order(self, *order):
        self.order = order

    def add_info(self, info):
        """
        Add strings of additional info to the report
        """
        self.infos.append(info)

    @property
    def group_dict(self):
        data = DataSet(self.data)

        if not self.order:
            self.order = ['id']
        data.sort(*self.order)

        if self.filter_funcs or self.filter_pairs:
            data = data.filtered(*self.filter_funcs, **self.filter_pairs)

        group_dict = data.group_dict(*self.grouping)
        return group_dict

    def _get_data(self):
        """
        The data is reloaded for every attribute, but read only once from disk
        """
        combined_props_file = os.path.join(self.eval_dir, 'properties')
        if not os.path.exists(combined_props_file):
            msg = 'Properties file not found at %s'
            logging.error(msg % combined_props_file)
            sys.exit(1)
        dump_path = os.path.join(self.eval_dir, 'data_dump')
        logging.info('Reading properties file without parsing')
        properties_contents = open(combined_props_file).read()
        logging.info('Calculating properties hash')
        new_checksum = hashlib.md5(properties_contents).digest()
        # Reload when the properties file changed or when no dump exists
        reload = True
        if os.path.exists(dump_path):
            logging.info('Reading data dump')
            old_checksum, data = cPickle.load(open(dump_path, 'rb'))
            logging.info('Reading data dump finished')
            reload = (not old_checksum == new_checksum)
            logging.info('Reloading: %s' % reload)
        if reload:
            data = DataSet()
            logging.info('Reading properties file')
            combined_props = tools.Properties(combined_props_file)
            logging.info('Reading properties file finished')
            for run_id, run in sorted(combined_props.items()):
                data.append(**run)
            logging.info('Finished turning properties into dataset')
            # Pickle data for faster future use
            cPickle.dump((new_checksum, data), open(dump_path, 'wb'),
                         cPickle.HIGHEST_PROTOCOL)
            logging.info('Wrote data dump')
        return data

    def name(self):
        name = os.path.basename(self.eval_dir)
        if len(self.foci) == 1:
            name += '-' + self.foci[0]
        return name

    def _get_table(self, focus):
        raise Exception('Not implemented')

    def write(self):
        doc = Document(title=self.name())
        string = str(self)

        if not string:
            logging.info('No tables generated. '
                         'This happens when no significant changes occured. '
                         'Therefore no output file has been created')
            return

        doc.add_text(string)
        self.output = doc.render(self.output_format, {'toc': 1})

        if not self.dry:
            ext = self.output_format.replace('xhtml', 'html')
            basename = self.name() + '.' + ext
            self.output_file = os.path.join(self.report_dir, basename)
            with open(self.output_file, 'w') as file:
                output_uri = 'file://' + os.path.abspath(self.output_file)
                logging.info('Writing output to %s' % output_uri)
                file.write(self.output)

    def open(self):
        """
        If the --open parameter is set, tries to open the report
        """
        if not self.open_report or not os.path.exists(self.output_file):
            return

        import subprocess
        dir, filename = os.path.split(self.output_file)
        os.chdir(dir)
        if self.output_format == 'tex':
            subprocess.call(['pdflatex', filename])
            filename = filename.replace('tex', 'pdf')
        subprocess.call(['xdg-open', filename])

        # Remove unnecessary files
        extensions = ['aux', 'log']
        filename_prefix, old_ext = os.path.splitext(os.path.basename(filename))
        for ext in extensions:
            try:
                os.remove(filename_prefix + '.' + ext)
            except OSError:
                pass

    def __str__(self):
        res = ''
        for info in self.infos:
            res += '- %s\n' % info
        if self.infos:
            res += '\n\n====================\n'

        # list of (attribute, table) pairs
        tables = []

        for focus in self.foci:
            self.data = self.orig_data.copy()
            try:
                table = self._get_table(focus)
                if table:
                    # We return None for a table if we don't want to add it
                    print table
                    tables.append((focus, table))
            except TypeError, err:
                logging.info('Omitting attribute "%s" (%s)' % (focus, err))

        if not tables:
            return ''

        for attribute, table in tables:
            res += '+ %s +\n%s\n' % (attribute, table)

        return res


class Table(collections.defaultdict):
    def __init__(self, title='', highlight=True, min_wins=True,
                 numeric_rows=False):
        collections.defaultdict.__init__(self, dict)

        self.title = title
        self.highlight = highlight
        self.min_wins = min_wins
        self.numeric_rows = numeric_rows

    def add_cell(self, row, col, value):
        self[row][col] = value

    @property
    def rows(self):
        special_rows = ['SUM', 'AVG', 'GM']
        rows = self.keys()
        # Let the sum, etc. rows be the last ones
        rows = ['zzz' + row if row.upper() in special_rows else row for row in rows]
        tools.natural_sort(rows)
        rows = [row[3:] if row.startswith('zzz') else row for row in rows]
        return rows

    @property
    def cols(self):
        cols = []
        for dict in self.values():
            for key in dict.keys():
                if key not in cols:
                    cols.append(key)

        tools.natural_sort(cols)
        return cols

    def get_cells_in_row(self, row):
        return [self[row][col] for col in self.cols]

    def get_comparison(self, comparator=cmp):
        """
        || expanded                      | fF               | yY              |
        | **prob01.pddl**                | 21               | 16              |
        | **prob02.pddl**                | 38               | 24              |
        | **prob03.pddl**                | 59               | 32              |
        ==>
        returns ((fF, yY), (0, 0, 3)) [wins, draws, losses]
        """
        assert len(self.cols) == 2, 'Please specify 2 configs'

        sums = [0, 0, 0]

        for row in self.rows:
            for col1, col2 in combinations(self.cols, 2):
                val1 = self[row][col1]
                val2 = self[row][col2]
                cmp_value = comparator(val1, val2)
                sums[cmp_value + 1] += 1

        return (self.cols, sums)

    def get_row(self, row, values=None):
        '''
        values has to be sorted by the corresponding column names
        '''
        if values is None:
            values = []
            for col in self.cols:
                values.append(self.get(row).get(col))

        only_one_value = len(set(values)) == 1

        # Filter out None values
        real_values = filter(bool, values)

        if real_values:
            min_value = min(real_values)
            max_value = max(real_values)
        else:
            min_value = max_value = 'undefined'

        min_wins = self.min_wins

        text = ''
        if self.numeric_rows:
            text += '| %-30s ' % (row)
        else:
            text += '| %-30s ' % ('**' + row + '**')
        for value in values:
            is_min = (value == min_value)
            is_max = (value == max_value)
            if self.highlight and only_one_value:
                value_text = '{{%s|color:Gray}}' % value
            elif self.highlight and (min_wins and is_min or
                                        not min_wins and is_max):
                value_text = '**%s**' % value
            else:
                value_text = str(value)
            text += '| %-16s ' % value_text
        text += '|\n'
        return text

    def __str__(self):
        """
        {'zenotravel': {'yY': 17, 'fF': 21}, 'gripper': {'yY': 72, 'fF': 118}}
        ->
        || expanded        | fF               | yY               |
        | **gripper     ** | 118              | 72               |
        | **zenotravel  ** | 21               | 17               |
        """
        text = '|| %-29s | ' % self.title

        rows = self.rows
        cols = self.cols

        # Escape config names to prevent unvoluntary markup
        text += ' | '.join('%-16s' % ('""%s""' % col) for col in cols) + ' |\n'
        for row in rows:
            text += self.get_row(row)
        return text


if __name__ == "__main__":
    logging.error('Please import this module from another script')
