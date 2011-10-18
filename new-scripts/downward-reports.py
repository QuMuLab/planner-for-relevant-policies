#! /usr/bin/env python
"""
Module that permits generating downward reports by reading properties files
"""

from __future__ import with_statement, division

import sys
import os
import logging
from collections import defaultdict
import itertools

import tools
import downward_suites
from external.datasets import missing, not_missing
import reports
from reports import Report, ReportArgParser, Table


REPORT_TYPES = {'abs': 'AbsoluteReport',
                'any': 'AnyAttributeReport',
                'iter': 'IterativeReport',
                'rel': 'RelativeReport',
                'scatter': 'ScatterPlotReport',
                'suite': 'SuiteReport'
                }


# Create a parser only for parsing the report type
report_type_parser = tools.ArgParser(add_help=False)
report_type_parser.epilog = ('NOTE: The help output may depend on the already '
                             'selected options')
report_type_parser.add_argument('-r', '--report', default='abs',
                                choices=sorted(REPORT_TYPES.keys()),
                                help='Select a report type')


class PlanningTable(Table):
    def __init__(self, *args, **kwargs):
        Table.__init__(self, *args, **kwargs)

        if self.title in ['search_time', 'total_time']:
            self.add_summary_function('GEOMETRIC MEAN', reports.gm)
        else:
            self.add_summary_function('SUM', sum)

        if 'score' in self.title:
            # When summarising score results from multiple domains we show
            # normalised averages so that each domain is weighed equally.
            self.add_summary_function('AVERAGE', reports.avg)


class PlanningReport(Report):
    def __init__(self, parser=ReportArgParser(parents=[report_type_parser])):
        parser.add_argument('-c', '--configs', type=tools.csv,
            help='only use specified configurations (e.g. WORK-ou,WORK-yY). '
                 'If none specified, use all found configs')
        parser.add_argument('-s', '--suite', type=tools.csv,
            help=downward_suites.HELP)

        Report.__init__(self, parser)

        if self.configs:
            self.name_parts.append('+'.join(self.configs))
        if self.suite:
            self.name_parts.append('+'.join(self.suite))

        if self.suite:
            self.problems = downward_suites.build_suite(self.suite)
        else:
            self.problems = []

        def filter_by_problem(run):
            """
            If suite is set, only process problems from the suite,
            otherwise process all problems
            """
            return any(prob.domain == run['domain'] and
                       prob.problem == run['problem'] for prob in self.problems)

        def filter_by_config(run):
            """
            If configs is set, only process those configs, otherwise process
            all configs
            """
            return any(config == run['config'] for config in self.configs)

        filter_funcs = []
        if self.configs:
            filter_funcs.append(filter_by_config)
        if self.problems:
            filter_funcs.append(filter_by_problem)
        if filter_funcs:
            self.data.filter(*filter_funcs)

    def get_text(self):
        # list of (attribute, table) pairs
        tables = []
        for attribute in self.attributes:
            logging.info('Creating table for %s' % attribute)
            table = self._get_table(attribute)
            # We return None for a table if we don't want to add it
            if table:
                tables.append((attribute, str(table)))

        return ''.join(['+ %s +\n%s\n' % (attr, table)
                        for (attr, table) in tables])

    def get_configs(self):
        """Return the list of configs."""
        return list(set([run['config'] for run in self.data]))

    def _get_empty_table(self, attribute):
        '''
        Returns an empty table. Used and filled by subclasses.
        '''
        # Decide whether we want to highlight minima or maxima
        max_attribute_parts = ['score', 'initial_h_value', 'coverage',
                               'quality']
        min_wins = True
        for attr_part in max_attribute_parts:
            if attr_part in attribute:
                min_wins = False
        table = PlanningTable(attribute, min_wins=min_wins)
        return table


class AbsoluteReport(PlanningReport):
    """
    Write an absolute report about the attribute attribute, e.g.

    || expanded        | fF               | yY               |
    | **gripper     ** | 118              | 72               |
    | **zenotravel  ** | 21               | 17               |
    """
    def __init__(self, parser=ReportArgParser(parents=[report_type_parser])):
        parser.add_argument('--res', default='domain', dest='resolution',
            help='resolution of the report',
            choices=['domain', 'problem'])

        # Apply previously set defaults
        parser.set_defaults(**parser._defaults)

        PlanningReport.__init__(self, parser)

        self.name_parts.append(self.resolution[0])

        # The domain-wise sum of the values for coverage and *_error even makes
        # sense if not all configs have values for those attributes.
        self.absolute_attributes = [attr for attr in self.all_attributes
                                    if attr.endswith('_error')]
        self.absolute_attributes.append('coverage')

        # Save the unfiltered groups for faster retrieval
        if self.resolution == 'domain':
            self.orig_groups = self.data.groups('config', 'domain')
        else:
            self.orig_groups = self.data.groups('config', 'domain', 'problem')
        self.orig_groups_domain_prob = self.data.groups('domain', 'problem')

    def _get_filtered_groups(self, attribute):
        """
        for an attribute include or ignore problems for which not all configs
        have this attribute.
        """
        logging.info('Filtering run groups where %s is missing' % attribute)
        del_probs = set()
        for (domain, problem), group in self.orig_groups_domain_prob:
            if any(value is missing for value in group[attribute]):
                del_probs.add(domain + problem)

        def delete_runs_with_missing_attributes(run):
            return not run['domain'] + run['problem'] in del_probs

        data = self.data.filtered(delete_runs_with_missing_attributes)

        if self.resolution == 'domain':
            return data.groups('config', 'domain')
        else:
            return data.groups('config', 'domain', 'problem')

    def _get_group_func(self, attribute):
        """Decide on a group function for this attribute."""
        if 'score' in attribute:
            return 'average', reports.avg
        elif attribute in ['search_time', 'total_time']:
            return 'geometric mean', reports.gm
        return 'sum', sum

    def _get_table(self, attribute):
        table = PlanningReport._get_empty_table(self, attribute)
        func_name, func = self._get_group_func(attribute)

        # If we don't have to filter the runs, we can use the saved group_dict
        if (self.resolution == 'problem' or
            attribute in self.absolute_attributes):
            groups = self.orig_groups
        else:
            groups = self._get_filtered_groups(attribute)
            table.info.append('Only instances where all configurations have a '
                              'value for "%s" are considered.' % attribute)
            table.info.append('Each table entry gives the %s of "%s" for that '
                              'domain.' % (func_name, attribute))
            summary_names = [name.lower()
                             for name, sum_func in table.summary_funcs]
            if len(summary_names) == 1:
                table.info.append('The last row gives the %s across all '
                                  'domains.' % summary_names[0])
            elif len(summary_names) > 1:
                table.info.append('The last rows give the %s across all '
                                  'domains.' % ' and '.join(summary_names))

        def show_missing_attribute_msg(name):
            msg = '%s: The attribute "%s" was not found. ' % (name, attribute)
            logging.debug(msg)

        if self.resolution == 'domain':
            for (config, domain), group in groups:
                values = filter(not_missing, group[attribute])
                if not values:
                    show_missing_attribute_msg(config + '-' + domain)
                    continue
                num_instances = len(group.group_dict('problem'))
                table.add_cell('%s (%s)' % (domain, num_instances), config,
                                            func(values))
        elif self.resolution == 'problem':
            for (config, domain, problem), group in groups:
                value = group.get_single_value(attribute)
                name = domain + ':' + problem
                if value is missing:
                    show_missing_attribute_msg(name)
                    table.add_cell(name, config, None)
                else:
                    table.add_cell(name, config, value)
        return table


class RelativeReport(AbsoluteReport):
    """
    Write a relative report about the focus attribute, e.g.

    || expanded        | fF               | yY               |
    | **gripper     ** | 1.0              | 0.6102           |
    | **zenotravel  ** | 1.0              | 0.8095           |
    """
    def __init__(self, parser=ReportArgParser(parents=[report_type_parser])):
        parser.add_argument('--rel-change', default=0, type=int,
            help='percentage that the value must have changed between two '
                'configs to be appended to the result table')
        parser.add_argument('--abs-change', default=0.0, type=float,
            help='only add pairs of values to the result if their absolute '
                 'difference is bigger than this number')

        AbsoluteReport.__init__(self, parser=parser)

        configs = self.get_configs()
        if not len(configs) == 2:
            sys.exit('Relative reports can only be performed for 2 configs. '
                     'Selected configs: "%s"' % configs)

    def _get_table(self, attribute):
        table = AbsoluteReport._get_table(self, attribute)
        quotient_col = {}
        percent_col = {}

        # Filter those rows which have no significant changes
        for row in table.rows:
            val1, val2 = table.get_row(row)

            # Handle cases where one value is not present (None) or zero
            if not val1 or not val2:
                quotient_col[row] = '---'
                continue

            quotient = val2 / val1
            percent_change = abs(quotient - 1.0) * 100
            abs_change = abs(val1 - val2)

            if (percent_change >= self.rel_change and
                abs_change >= self.abs_change):
                quotient_col[row] = round(quotient, 4)
                percent_col[row] = round(percent_change, 4)
            else:
                del table[row]

        # Add table also if there were missing cells
        if len(quotient_col) == 0:
            logging.info('No changes above for "%s"' % attribute)
            return None

        table.add_col('ZZ1-SORT:Factor', quotient_col)
        #table.add_col('ZZ2-SORT:%-Change', percent_col)
        table.highlight = False
        table.summary_funcs = []
        return table


class AnyAttributeReport(PlanningReport):
    """
    Write an any-attribute (anytime, any-expanded, ...) report
    || time            | fF               | yY               |
    | 10               | 10               | 12               |
    | 20               | 21               | 17               |
    """
    def __init__(self, parser=ReportArgParser(parents=[report_type_parser])):
        parser.set_defaults(commandline_attributes=['search_time'])
        parser.add_argument('--min-value', type=int, default=0)
        parser.add_argument('--max-value', type=int, default=1800)
        parser.add_argument('--step', type=int, default=5)

        PlanningReport.__init__(self, parser)

        if len(self.attributes) != 1:
            logging.error("Please select exactly one attribute for an "
                          "any-attribute report")
            sys.exit(1)

    def _get_table(self, attribute):
        table = PlanningTable(attribute, highlight=False, numeric_rows=True)

        for config, group in self.data.group_dict('config').items():
            group.filter(coverage=1)
            group.sort(attribute)
            for time_limit in xrange(self.min_value, self.max_value + 1,
                                     self.step):
                table.add_cell(str(time_limit), config,
                    len(group.filtered(lambda di: di[attribute] <= time_limit)))
        return table


class IterativeReport(AbsoluteReport):
    def __init__(self, parser=ReportArgParser(parents=[report_type_parser])):
        parser.set_defaults(resolution='problem')
        AbsoluteReport.__init__(self, parser=parser)
        assert self.resolution == 'problem'
        if not self.commandline_attributes:
            self.attributes = self._get_iterative_attributes()

    def _get_iterative_attributes(self):
        return [attr for attr in self.all_attributes if attr.endswith('_all')]

    def _get_table(self, attribute):
        table = AbsoluteReport._get_table(self, attribute)

        # Turn all lists of values into comma separated strings
        for row in table.rows:
            for col in table.cols:
                table[row][col] = ', '.join(str(val) for val in table[row][col])

        table.highlight = False
        table.summary_funcs = []
        return table


class ScatterPlotReport(AbsoluteReport):
    def __init__(self, parser=ReportArgParser()):
        parser.set_defaults(resolution='problem')
        AbsoluteReport.__init__(self, parser)

        assert len(self.get_configs()) == 2, self.get_configs()
        assert len(self.attributes) == 1, self.attributes

        self.extension = 'png'

    def write_plot(self, attribute, filename):
        try:
            from matplotlib.backends.backend_agg import FigureCanvasAgg
            from matplotlib.figure import Figure
        except ImportError, err:
            logging.error('matplotlib could not be found: %s' % err)
            sys.exit(1)

        table = self._get_table(attribute)
        cfg1, cfg2 = table.cols
        columns = table.get_columns()
        assert len(columns[cfg1]) == len(columns[cfg2]), columns

        # It may be the case that no values are found
        try:
            max_value = max(columns[cfg1] + columns[cfg2])
        except ValueError:
            pass

        if max_value is None or max_value <= 0:
            logging.info('Found no valid datapoints for the plot.')
            print table
            sys.exit()

        # Make the value bigger to separate it from normal values
        missing_val = tools.round_to_next_power_of_ten(max_value * 10)

        values1 = []
        values2 = []
        for val1, val2 in zip(columns[cfg1], columns[cfg2]):
            if val1 is None and val2 is None:
                continue
            if val1 is None:
                val1 = missing_val
            if val2 is None:
                val2 = missing_val
            values1.append(val1)
            values2.append(val2)

        plot_size = missing_val * 1.25

        # Create a figure with size 6 x 6 inches
        fig = Figure(figsize=(10, 10))

        # Create a canvas and add the figure to it
        canvas = FigureCanvasAgg(fig)
        ax = fig.add_subplot(111)

        # Make a descriptive title and set axis labels
        suite = ' (%s)' % ','.join(self.suite) if self.suite else ''
        title = ''.join([attribute, suite, ' by ', self.resolution])
        ax.set_title(title, fontsize=14)
        ax.set_xlabel(cfg1, fontsize=12)
        ax.set_ylabel(cfg2, fontsize=12)

        # Display grid
        ax.grid(b=True, linestyle='-', color='0.75')

        # Generate the scatter plot
        ax.scatter(values1, values2, s=20, marker='o', c='r');

        # Plot a diagonal black line. Starting at (0,0) often raises errors.
        ax.plot([0.001, plot_size], [0.001, plot_size], 'k')

        linear_attributes = ['cost', 'coverage', 'plan_length']
        if attribute not in linear_attributes:
            logging.info('Using logarithmic scaling')
            ax.set_xscale('symlog')
            ax.set_yscale('symlog')

        ax.set_xlim(0, plot_size)
        ax.set_ylim(0, plot_size)

        # We do not want the default formatting that gives zeros a special font
        for axis in (ax.xaxis, ax.yaxis):
            formatter = axis.get_major_formatter()
            old_format_call = formatter.__call__
            def new_format_call(x, pos):
                if x == 0:
                    return 0
                if x == missing_val:
                    return 'Missing' # '$\mathdefault{None^{\/}}$' no effect
                return old_format_call(x, pos)
            formatter.__call__ = new_format_call

        # Save the generated scatter plot to a PNG file
        canvas.print_figure(filename, dpi=100)

    def write(self):
        if self.dry:
            return

        filename = self.get_filename()
        if not filename.endswith('.png'):
            filename += '.png'
        self.write_plot(self.attributes[0], filename)
        logging.info('Wrote file://%s' % filename)


class SuiteReport(PlanningReport):
    """
    Write a list of problems to a file

    We do not need any markup processing or loop over attributes here,
    so the build and write methods are implemented right here.

    The data is filtered by the filter functions given on the commandline,
    all the runs are checked whether they pass the filters and the remaining
    runs are sorted, the duplicates are removed and the resulting list of
    problems is written to an output file
    """
    def __init__(self, *args, **kwargs):
        PlanningReport.__init__(self, *args, **kwargs)
        self.extension = 'py'

    def build(self):
        if len(self.data) == 0:
            sys.exit('No problems match those filters')
        problems = [run['domain'] + ':' + run['problem'] for run in self.data]
        # Sort and remove duplicates
        problems = sorted(set(problems))
        problems = ['        "%s",\n' % problem for problem in problems]
        output = ('def suite():\n    return [\n%s    ]\n' % ''.join(problems))
        print '\nSUITE:'
        print output
        return output


if __name__ == "__main__":
    with tools.timing("Create report"):
        known_args, remaining_args = report_type_parser.parse_known_args()

        # delete parsed args
        sys.argv = [sys.argv[0]] + remaining_args

        report_name = REPORT_TYPES[known_args.report]
        logging.info('Report: %s' % report_name)

        # Instantiate selected Report
        report = globals().get(report_name)()

        # Copy the report type
        report.report_type = known_args.report

        report.write()
        report.open()
