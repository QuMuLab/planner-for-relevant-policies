#! /usr/bin/env python
"""
Module that permits generating reports by reading properties files
"""

from __future__ import with_statement, division

import os
import sys
import logging
import collections
import cPickle
import hashlib
import subprocess
import operator
from collections import defaultdict

import tools
from markup import Document
from external import txt2tags
from external.datasets import missing


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

        self.add_argument('eval_dir', type=self.directory,
                    help='path to results directory')

        self.add_argument('--outfile', default=None,
                    help='if not set, the report will be written to a file '
                    'in %s.' % tools.REPORTS_DIR)

        self.add_argument('-a', '--attributes', type=tools.csv,
                    metavar='ATTR',
                    help='the analyzed attributes (e.g. "expanded"). '
                    'If omitted, use all found numerical attributes')

        self.add_argument('--format', dest='output_format', default='html',
                    help='format of the output file',
                    choices=sorted(txt2tags.TARGETS))

        self.add_argument('--filter', dest='filters', type=tools.csv,
                default=[], help='filters will be applied as follows: '
                'expanded:lt:100 -> only process if run[expanded] < 100')

        self.add_argument('--dry', default=False, action='store_true',
                    help='do not write anything to the filesystem')

        self.add_argument('--show-attributes', action='store_true',
                    help='show a list of available attributes and exit')

        self.add_argument('--open', default=False, action='store_true',
                    dest='open_report',
                    help='open the report file after writing it')

    def parse_args(self, *args, **kwargs):
        args = tools.ArgParser.parse_args(self, *args, **kwargs)

        args.eval_dir = os.path.normpath(os.path.abspath(args.eval_dir))
        logging.info('Eval dir: "%s"' % args.eval_dir)

        if not args.eval_dir.endswith('eval'):
            msg = ('The source directory does not end with eval. '
                   'Are you sure you this is an evaluation directory? (Y/N): ')
            answer = raw_input(msg)
            if not answer.upper() == 'Y':
                sys.exit()

        return args


class Report(object):
    """
    Base class for all reports
    """
    def __init__(self, parser=ReportArgParser()):
        # Give all the options to the report instance
        parser.parse_args(namespace=self)

        self.report_type = 'report'
        self.data = self._load_data()

        self.all_attributes = sorted(self.data.get_attributes())

        if self.show_attributes:
            print '\nAvailable attributes: %s' % self.all_attributes
            sys.exit()

        if not self.attributes:
            self.attributes = self.get_numerical_attributes()
        else:
            # Make sure that all selected attributes are present in the dataset
            not_found = set(self.attributes) - set(self.all_attributes)
            if not_found:
                logging.error('The following attributes are not present in '
                              'the dataset: %s' % sorted(not_found))
                sys.exit(1)
        logging.info('Selected Attributes: %s' % self.attributes)

        if self.filters:
            self._apply_filters()

        self.infos = []

        self.extension = None

        self.name_parts = []
        if len(self.attributes) == 1:
            self.name_parts.append(self.attributes[0])
        if self.filters:
            self.name_parts.append('+'.join([f.replace(':', '_')
                                             for f in self.filters]))

    def get_numerical_attributes(self):
        def is_numerical(attribute):
            for val in self.data.key(attribute)[0]:
                if val is missing:
                    continue
                return type(val) in [int, float]
            logging.info("Attribute %s is missing in all runs." % attribute)
            # Include the attribute nonetheless
            return True

        return [attr for attr in self.all_attributes if is_numerical(attr)]

    def add_info(self, info):
        """
        Add strings of additional info to the report
        """
        self.infos.append(info)

    def get_name(self):
        return ('%s-%s-%s' % (os.path.basename(self.eval_dir), self.report_type,
                             '-'.join(self.name_parts))).rstrip('-')

    def get_filename(self):
        if self.outfile:
            return os.path.abspath(self.outfile)
        ext = self.extension or self.output_format.replace('xhtml', 'html')
        return os.path.join(tools.REPORTS_DIR, '%s.%s' % (self.get_name(), ext))

    def get_text(self):
        """
        This method should be overwritten in subclasses.
        """
        table = Table(highlight=False)
        for run_id, run_group in sorted(self.data.groups('id-string')):
            assert len(run_group) == 1, run_group
            run = run_group.items[0]
            del run['id']
            for key, value in run.items():
                if type(value) is list:
                    run[key] = '-'.join([str(item) for item in value])
            table.add_row(run_id, run)
        return str(table)

    def write(self):
        self.write_to_disk(self.build())

    def build(self):
        doc = Document(title=self.get_name())
        for info in self.infos:
            doc.add_text('- %s' % info)
        if self.infos:
            doc.add_text('\n\n====================\n')

        text = self.get_text()

        if not text:
            logging.info('No tables were generated. '
                         'This happens when no significant changes occured or '
                         'if for all attributes and all problems never all '
                         'configs had a value for this attribute in a '
                         'domain-wise report. Therefore no output file is '
                         'created.')
            return ''

        doc.add_text(text)
        print 'REPORT MARKUP:\n'
        print doc
        return doc.render(self.output_format, {'toc': 1})

    def write_to_disk(self, content):
        if self.dry or not content:
            return

        filename = self.get_filename()
        tools.makedirs(os.path.dirname(filename))
        with open(filename, 'w') as file:
            file.write(content)
            logging.info('Wrote file://%s' % filename)

    def open(self):
        """
        If the --open parameter is set, tries to open the report
        """
        filename = self.get_filename()
        if not self.open_report or not os.path.exists(filename):
            return

        dir, filename = os.path.split(filename)
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
        """
        If numeric_rows is True, we do not make the first column bold.
        """
        collections.defaultdict.__init__(self, dict)

        self.title = title
        self.highlight = highlight
        self.min_wins = min_wins
        self.numeric_rows = numeric_rows

        self.summary_funcs = []
        self.column_order = {}

        self._cols = None

    def add_cell(self, row, col, value):
        self[row][col] = value
        self._cols = None

    def add_row(self, row_name, row):
        """row must map column names to the value in row "row_name"."""
        self[row_name] = row
        self._cols = None

    def add_col(self, col_name, col):
        """col must map row names to values."""
        for row_name, value in col.items():
            self[row_name][col_name] = value
        self._cols = None

    @property
    def rows(self):
        # Let the sum, etc. rows be the last ones
        return tools.natural_sort(self.keys())

    @property
    def cols(self):
        if self._cols:
            return self._cols
        col_names = set()
        for row in self.values():
            col_names |= set(row.keys())
        self._cols = tools.natural_sort(col_names)
        return self._cols

    def get_row(self, row):
        return [self[row].get(col, None) for col in self.cols]

    def get_rows(self):
        return [(row, self.get_row(row)) for row in self.rows]

    def get_columns(self):
        """
        Returns a mapping from column name to the list of values in that column.
        """
        values = defaultdict(list)
        for row in self.rows:
            for col in self.cols:
                values[col].append(self[row].get(col))
        return values

    def get_row_markup(self, row_name, row=None):
        """
        If given, row must be a dictionary mapping column names to the value in
        row "row_name".
        """
        if row is None:
            row = self[row_name]

        values = []
        for col in self.cols:
            values.append(row.get(col))

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
            text += '| %-30s ' % (row_name)
        else:
            text += '| %-30s ' % ('**' + row_name + '**')
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

    def add_summary_function(self, name, func):
        """
        This function adds a bottom row with the values func(column_values) for
        each column. Func can be e.g. sum, reports.avg, reports.gm
        """
        self.summary_funcs.append((name, func))

    def __str__(self):
        """
        {'zenotravel': {'yY': 17, 'fF': 21}, 'gripper': {'yY': 72, 'fF': 118}}
        ->
        || expanded        | fF               | yY               |
        | **gripper     ** | 118              | 72               |
        | **zenotravel  ** | 21               | 17               |
        """
        text = '|| %-29s | ' % self.title

        def get_col_markup(col):
            # Allow custom sorting of the column names
            if '-SORT:' in col:
                sorting, col = col.split('-SORT:')
            # Escape config names to prevent unvoluntary markup
            return '%-16s' % ('""%s""' % col)

        text += ' | '.join(get_col_markup(col) for col in self.cols) + ' |\n'
        for row in self.rows:
            text += self.get_row_markup(row)
        for name, func in self.summary_funcs:
            summary_row = dict([(col, func(content)) for col, content in
                                self.get_columns().items()])
            text += self.get_row_markup(name, summary_row)
        return text


if __name__ == "__main__":
    report = Report()
    report.write()
