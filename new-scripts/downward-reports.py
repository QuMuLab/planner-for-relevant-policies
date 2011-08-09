#! /usr/bin/env python
"""
Module that permits generating downward reports by reading properties files
"""

from __future__ import with_statement, division

import sys
import os
import logging
from collections import defaultdict

import tools
import downward_suites
from external.datasets import missing, not_missing
import reports
from reports import Report, ReportArgParser, Table


REPORT_TYPES = {'abs': 'AbsoluteReport',
                'rel': 'RelativeReport',
                'any': 'AnyAttributeReport',
                'scatter': 'ScatterPlotReport',
                'suite': 'SuiteReport'
                }


# Create a parser only for parsing the report type
report_type_parser = tools.ArgParser(add_help=False)
report_type_parser.epilog = ('Note: The help output may depend on the already '
                             'selected options')
report_type_parser.add_argument('-r', '--report', default='abs',
            choices=sorted(REPORT_TYPES.keys()),
            help='Select a report type')


class PlanningTable(Table):
    def __init__(self, *args, **kwargs):
        Table.__init__(self, *args, **kwargs)

        self.add_summary_function(sum)
        if 'score' in self.title:
            # When summarising score results from multiple domains we show
            # normalised averages so that each domain is weighed equally.
            self.add_summary_function(reports.avg)


class PlanningReport(Report):
    def __init__(self, parser=ReportArgParser(parents=[report_type_parser])):
        parser.add_argument('-c', '--configs', type=tools.csv,
            help='only use specified configurations (e.g. WORK-ou,WORK-yY). '
                 'If none specified, use all found configs')

        parser.add_argument('-s', '--suite', type=tools.csv,
            help=downward_suites.HELP)

        parser.add_argument('--res', default='domain', dest='resolution',
            help='resolution of the report',
            choices=['domain', 'problem'])

        parser.add_argument('--missing', default='auto',
            dest='handle_missing_attrs', choices=['include', 'ignore', 'auto'],
            help='for an attribute include or ignore problems for which not '
                'all configs have this attribute. "auto" includes those '
                'problems in the detailed view and ignores them in the '
                'domain-summary reports')

        Report.__init__(self, parser)

        # For some attributes only compare commonly solved tasks
        self.commonly_solved_attributes = [
                'cost', 'expanded', 'expansions', 'generated', 'memory',
                'plan_length', 'search_time', 'total_time']
        info = ('The attributes %s are handled as follows:\n'
                'If in a group of configs not all configs have a value for '
                'the attribute, the concerning runs are only evaluated if '
                '"``--missing``" is set to "include" or if "``--missing``" is '
                'set to "auto" (default) and the resolution is "problem"')
        info %= ', '.join(self.commonly_solved_attributes)
        self.add_info(info)

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

        # Save the unfiltered group_dicts for faster retrieval
        if self.resolution == 'domain':
            self.orig_group_dict = self.data.group_dict('config', 'domain')
        else:
            self.orig_group_dict = self.data.group_dict('config', 'domain', 'problem')
        self.orig_group_dict_domain_prob = self.data.group_dict('domain', 'problem')

    def get_text(self):
        # list of (attribute, table) pairs
        tables = []
        for attribute in self.attributes:
            try:
                table = self._get_table(attribute)
                # We return None for a table if we don't want to add it
                if table:
                    tables.append((attribute, table))
            except TypeError, err:
                logging.info('Omitting attribute "%s" (%s)' % (attribute, err))

        return ''.join(['+ %s +\n%s\n' % (attr, table) for (attr, table) in tables])

    def get_name(self):
        name = Report.get_name(self)
        if self.configs:
            name += '-' + '+'.join(self.configs)
        if self.suite:
            name += '-' + '+'.join(self.suite)
        name += '-' + self.resolution[0]
        name += '-' + self.report_type
        return name

    def get_configs(self):
        """Return the list of configs."""
        return list(set([run['config'] for run in self.data]))

    def _must_filter_common_attributes(self, attribute):
        """For some reports include all runs"""
        return not (attribute not in self.commonly_solved_attributes or
                    self.handle_missing_attrs == 'include' or
                    (self.handle_missing_attrs == 'auto' and
                     self.resolution == 'problem'))

    def _filter_common_attributes(self, attribute):
        """
        for an attribute include or ignore problems for which not
        all configs have this attribute. --missing=auto includes those
        problems in the detailed view and ignores them in the
        domain-summary reports
        """
        # For some reports include all runs
        if not self._must_filter_common_attributes(attribute):
            return self.data

        logging.info('Filtering problems with missing attributes for runs')
        del_probs = set()
        for (domain, problem), group in self.orig_group_dict_domain_prob.items():
            if any(value is missing for value in group[attribute]):
                del_probs.add(domain + problem)

        def delete_runs_with_missing_attributes(run):
            return not run['domain'] + run['problem'] in del_probs

        return self.data.filtered(delete_runs_with_missing_attributes)

    def _get_empty_table(self, attribute):
        '''
        Returns an empty table. Used and filled by subclasses.
        '''
        # Decide whether we want to highlight minima or maxima
        max_attribute_parts = ['score', 'initial_h_value', 'coverage']
        min_wins = True
        for attr_part in max_attribute_parts:
            if attr_part in attribute:
                min_wins = False
        table = PlanningTable(attribute, min_wins=min_wins)
        return table

    def get_group_func(self, attribute):
        """Decide on a group function for this attribute."""
        if 'score' in attribute:
            return reports.avg
        elif attribute in ['search_time', 'total_time']:
            return reports.gm
        return sum


class AbsoluteReport(PlanningReport):
    """
    Write an absolute report about the attribute attribute, e.g.

    || expanded        | fF               | yY               |
    | **gripper     ** | 118              | 72               |
    | **zenotravel  ** | 21               | 17               |
    """
    def __init__(self, *args, **kwargs):
        PlanningReport.__init__(self, *args, **kwargs)

    def _get_table(self, attribute):
        table = PlanningReport._get_empty_table(self, attribute)
        func = self.get_group_func(attribute)

        # If we don't have to filter the runs, we can use the saved group_dict
        if self._must_filter_common_attributes(attribute):
            data = self._filter_common_attributes(attribute)
            if self.resolution == 'domain':
                group_dict = data.group_dict('config', 'domain')
            else:
                group_dict = data.group_dict('config', 'domain', 'problem')
        else:
            group_dict = self.orig_group_dict

        def show_missing_attribute_msg(name):
            msg = '%s: The attribute "%s" was not found. ' % (name, attribute)
            logging.debug(msg)

        if self.resolution == 'domain':
            for (config, domain), group in group_dict.items():
                values = filter(not_missing, group[attribute])
                if not values:
                    show_missing_attribute_msg(config + '-' + domain)
                    continue
                num_instances = len(group.group_dict('problem'))
                table.add_cell('%s (%s)' % (domain, num_instances), config, func(values))
        elif self.resolution == 'problem':
            for (config, domain, problem), group in group_dict.items():
                values = filter(not_missing, group[attribute])
                name = domain + ':' + problem
                if not values:
                    show_missing_attribute_msg(name)
                    continue
                assert len(values) <= 1, \
                    '%s occurs in results more than once' % name
                table.add_cell(name, config, func(values))
        return table


class RelativeReport(AbsoluteReport):
    """
    Write a relative report about the focus attribute, e.g.

    || expanded        | fF               | yY               |
    | **gripper     ** | 1.0              | 0.6102           |
    | **zenotravel  ** | 1.0              | 0.8095           |
    """
    def __init__(self, parser=ReportArgParser(parents=[report_type_parser])):
        parser.add_argument('--change', default=0, type=int,
            help='percentage that the value must have changed between two '
                'configs to be appended to the result table')

        AbsoluteReport.__init__(self, parser=parser)

        configs = self.get_configs()
        if not len(configs) == 2:
            sys.exit('Relative reports can only be performed for 2 configs. '
                     'Selected configs: "%s"' % configs)

    def _get_table(self, attribute):
        table = AbsoluteReport._get_table(self, attribute)
        quotient_col = {}

        # Filter those rows which have no significant changes
        for row in table.rows:
            val1, val2 = table.get_cells_in_row(row)

            # Handle cases where one value is not present (None) or zero
            if not val1 or not val2:
                quotient_col[row] = '---'
                continue

            quotient = val2 / val1
            percent_change = abs(quotient - 1.0) * 100

            if percent_change >= self.change:
                quotient_col[row] = round(quotient, 4)
            else:
                del table[row]

        # Add table also if there were missing cells
        if len(quotient_col) == 0:
            logging.info('No changes above %d%% for "%s"' % (self.change,
                                                             attribute))
            return None

        table.add_col('ZZZ-SORT:Factor', quotient_col)
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
        parser.set_defaults(attributes='search_time')
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
            for time_limit in xrange(self.min_value, self.max_value + 1, self.step):
                table.add_cell(str(time_limit), config,
                    len(group.filtered(lambda di: di[attribute] <= time_limit)))
        return table


class ScatterPlotReport(PlanningReport):
    def __init__(self, parser=ReportArgParser()):
        PlanningReport.__init__(self, parser)

        assert len(self.get_configs()) == 2, self.get_configs()
        assert len(self.attributes) == 1, self.attributes

    def get_name(self):
        name = os.path.basename(self.eval_dir)
        name += '-scatter-' + '+'.join(self.attributes)
        return name

    def write_plot(self, attribute, filename):
        try:
            from matplotlib.backends.backend_agg import FigureCanvasAgg
            from matplotlib.figure import Figure
        except ImportError, err:
            logging.error('matplotlib could not be found: %s' % err)
            sys.exit(1)

        cfg1, cfg2 = self.get_configs()
        all_values = defaultdict(list)
        for (domain, problem), group in self.data.group_dict('domain',
                                                             'problem').items():
            # Only add values if both configs have them
            prob_values = {}
            for (config), config_group in group.group_dict('config').items():
                val = config_group.get_single_value(attribute)
                if val is not missing:
                    prob_values[config] = val
            if len(prob_values) == 2:
                all_values[cfg1].append(prob_values[cfg1])
                all_values[cfg2].append(prob_values[cfg2])

        if not all_values:
            logging.info('Attribute "%s" was not found in any pair of runs' %
                         attribute)
            sys.exit(1)

        # Create a figure with size 6 x 6 inches
        fig = Figure(figsize=(10, 10))

        # Create a canvas and add the figure to it
        canvas = FigureCanvasAgg(fig)
        ax = fig.add_subplot(111)

        ax.set_title(attribute, fontsize=14)
        ax.set_xlabel(cfg1, fontsize=10)
        ax.set_ylabel(cfg2, fontsize=10)

        # Display grid
        ax.grid(b=True, linestyle='-', color='0.75')

        # Generate the scatter plot
        ax.scatter(*all_values.values(), s=20, marker='+');

        # Save the generated scatter plot to a PNG file
        canvas.print_figure(filename, dpi=500)

    def get_filename(self):
        return os.path.join(tools.REPORTS_DIR, self.get_name() + '.png')

    def write(self):
        if self.dry:
            return

        filename = self.outfile or self.get_filename()
        self.write_plot(self.attributes[0], filename)
        logging.info('Wrote file %s' % 'file://' + os.path.abspath(filename))


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

    def get_filename(self):
        exp_name = os.path.basename(self.eval_dir).replace('-eval', '')
        filters = '_'.join(self.filters).replace(':', '')
        parts = [exp_name, 'suite']
        if filters:
            parts.append(filters)
        return '_'.join(parts) + '.py'


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
