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
import subprocess
from collections import defaultdict

import tools
from markup import Document
from external import txt2tags


def avg(values):
    """Computes the arithmetic mean of a list of numbers.

    >>> print avg([20, 30, 70])
    40.0
    """
    return round(sum(values, 0.0) / len(values), 2)


def gm(values):
    """Computes the geometric mean of a list of numbers.

    >>> print gm([2, 8])
    4.0
    """
    assert len(values) >= 1
    exp = 1.0 / len(values)
    return round(tools.prod([val ** exp for val in values]), 2)


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

        self.add_argument('--filter', dest='filters', type=tools.csv,
                default=[], help='filters will be applied as follows: '
                'expanded:lt:100 -> only process if run[expanded] < 100')

        self.add_argument('--dry', default=False, action='store_true',
                    help='do not write anything to the filesystem')

        self.add_argument('--show_attributes', action='store_true',
                    help='show a list of available attributes and exit')

        self.add_argument('--open', default=False, action='store_true',
                    dest='open_report',
                    help='open the report file after writing it')

        self.add_argument('-a', '--attributes', type=tools.csv,
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

        self.data = self._load_data()

        attributes = sorted(self.data.get_attributes())

        if self.show_attributes:
            print '\nAvailable attributes: %s' % attributes
            sys.exit()

        if not self.attributes or self.attributes == 'all':
            self.attributes = attributes
        logging.info('Attributes: %s' % self.attributes)

        if self.filters:
            self._apply_filters()

        self.infos = []

    def add_info(self, info):
        """
        Add strings of additional info to the report
        """
        self.infos.append(info)

    def get_name(self):
        name = os.path.basename(self.eval_dir)
        if len(self.attributes) == 1:
            name += '-' + self.attributes[0]
        if self.filters:
            name += '-' + '+'.join([f.replace(':', '_') for f in self.filters])
        return name

    def get_filename(self):
        ext = self.output_format.replace('xhtml', 'html')
        return os.path.join(self.report_dir, self.get_name() + '.' + ext)

    def get_text(self):
        self.set_order('id-string')
        self.set_grouping('id-string')
        table = Table(highlight=False)
        for run_id, run_group in self.group_dict.items():
            assert len(run_group) == 1, run_group
            run = run_group.items[0]
            del run['id']
            for key, value in run.items():
                if type(value) is list:
                    run[key] = '-'.join([str(item) for item in value])
            table[run_id] = run
        return str(table)

    def write(self):
        doc = Document(title=self.get_name())
        for info in self.infos:
            doc.add_text('- %s\n' % info)
        if self.infos:
            doc.add_text('\n\n====================\n')

        text = self.get_text()

        if not text:
            logging.info('No tables generated. '
                         'This happens when no significant changes occured. '
                         'Therefore no output file has been created')
            return

        doc.add_text(text)
        print 'REPORT MARKUP:\n'
        print doc
        self.output = doc.render(self.output_format, {'toc': 1})

        if not self.dry:
            with open(self.get_filename(), 'w') as file:
                output_uri = 'file://' + os.path.abspath(self.get_filename())
                logging.info('Writing output to %s' % output_uri)
                file.write(self.output)

    def open(self):
        """
        If the --open parameter is set, tries to open the report
        """
        if not self.open_report or not os.path.exists(self.get_filename()):
            return

        dir, filename = os.path.split(self.get_filename())
        os.chdir(dir)
        if self.output_format == 'tex':
            subprocess.call(['pdflatex', filename])
            filename = filename.replace('tex', 'pdf')
        subprocess.call(['xdg-open', filename])

        # Remove unnecessary files
        extensions = ['aux', 'log']
        filename_prefix, old_ext = os.path.splitext(os.path.basename(filename))
        for ext in extensions:
            tools.remove(filename_prefix + '.' + ext)

    def _load_data(self):
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
            logging.info('Reading properties file')
            combined_props = tools.Properties(combined_props_file)
            logging.info('Reading properties file finished')
            data = combined_props.get_dataset()
            logging.info('Finished turning properties into dataset')
            # Pickle data for faster future use
            cPickle.dump((new_checksum, data), open(dump_path, 'wb'),
                         cPickle.HIGHEST_PROTOCOL)
            logging.info('Wrote data dump')
        return data

    def _apply_filters(self):
        """
        Filter strings have the form e.g.
        expanded:lt:100 or solved:eq:1 or generated:ge:2000
        """
        filter_funcs = []
        for s in self.filters:
            attribute, op, value = s.split(':')

            try:
                value = float(value)
            except ValueError:
                pass

            try:
                op = getattr(operator, op.lower())
            except AttributeError:
                logging.error('The operator module has no operator "%s"' % op)
                sys.exit()

            filter_funcs.append(lambda run: op(run[attribute], value))

        self.data.filter(*filter_funcs)


class Table(collections.defaultdict):
    def __init__(self, title='', highlight=True, min_wins=True,
                 numeric_rows=False):
        collections.defaultdict.__init__(self, dict)

        self.title = title
        self.highlight = highlight
        self.min_wins = min_wins
        self.numeric_rows = numeric_rows
        self.summaries = collections.defaultdict(dict)

    def add_cell(self, row, col, value):
        self[row][col] = value

    @property
    def rows(self):
        # Let the sum, etc. rows be the last ones
        return tools.natural_sort(self.keys())

    @property
    def cols(self):
        cols = set()
        for dict in self.values():
            for key in dict.keys():
                cols.add(key)

        return tools.natural_sort(cols)

    def get_cells_in_row(self, row):
        return [self[row][col] for col in self.cols]

    def get_column_contents(self):
        """
        Returns a mapping from column name to the list of values in that column.
        """
        values = defaultdict(list)
        for row in self.rows:
            for col, value in self[row].items():
                values[col].append(value)
        return values

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

    def add_summary_row(self, func):
        """
        This function adds a bottom row with the values func(column_values) for
        each column. Func can be e.g. sum, reports.avg, reports.gm
        """
        func_name = func.__name__.upper()
        for col, content in self.get_column_contents().items():
            self.summaries[func_name][col] = func(content)

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
        for summary, value_dict in self.summaries.items():
            text += self.get_row(summary, value_dict.values())
        return text


if __name__ == "__main__":
    report = Report()
    report.write()
