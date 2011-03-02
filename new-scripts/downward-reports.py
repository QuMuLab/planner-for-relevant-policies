#! /usr/bin/env python
"""
Module that permits generating downward reports by reading properties files
"""

from __future__ import with_statement, division

import sys
import os
import logging
import operator
from collections import defaultdict

import tools
import downward_suites
from external import datasets
from external.datasets import missing
import reports
from reports import Report, ReportArgParser, Table


# Create a parser only for parsing the report type
report_type_parser = tools.ArgParser(add_help=False)
report_type_parser.epilog = ('Note: The help output may depend on the already '
                             'selected options')
report_type_parser.add_argument('-r', '--report', default='abs',
            choices=['abs', 'cmp', 'any', 'suite'],
            help='Select a report type')


class PlanningTable(Table):
    def __init__(self, *args, **kwargs):
        Table.__init__(self, *args, **kwargs)

    def get_normalized_avg_row(self):
        """
        When summarising score results from multiple domains we show
        normalised averages such that each domain is weighed equally.
        """
        values = defaultdict(list)
        normal_rows = [row for row in self.rows if not row == 'SUM']
        for row in normal_rows:
            for col, value in self[row].items():
                values[col].append(value)
        averages = [reports.avg(val) for col, val in sorted(values.items())]
        text = self.get_row('NORMALIZED AVG', averages)
        return text

    def __str__(self):
        text = Table.__str__(self)
        if 'score' in self.title:
            text += self.get_normalized_avg_row()
        return text


class PlanningReport(Report):
    """
    """
    def __init__(self, parser=ReportArgParser(parents=[report_type_parser])):
        parser.add_argument('-c', '--configs', type=tools.csv,
            help='only use specified configurations (e.g. WORK-ou,WORK-yY). '
                 'If none specified, use all found configs')
        parser.add_argument('-s', '--suite', type=tools.csv,
            help=downward_suites.HELP)
        parser.add_argument('--res', default='domain', dest='resolution',
            help='resolution of the report',
            choices=['suite', 'domain', 'problem'])
        parser.add_argument('--filter', type=tools.csv, default=[],
            help='filters will be applied as follows: '
                'expanded:lt:100 -> only process if run[expanded] < 100')
        parser.add_argument('--missing', default='auto',
            dest='handle_missing_attrs', choices=['include', 'ignore', 'auto'],
            help='for an attribute include or ignore problems for which not '
                'all configs have this attribute. "auto" includes those '
                'problems in the detailed view and ignores them in the '
                'domain-summary reports')

        Report.__init__(self, parser)

        self.output = ''

        # For some attributes only compare commonly solved tasks
        self.commonly_solved_foci = [
                'cost', 'expanded', 'expansions', 'generated', 'memory',
                'plan_length', 'search_time', 'total_time']
        info = ('The attributes %s are handled as follows:\n'
                'If in a group of configs not all configs have a value for '
                'the attribute, the concerning runs are only evaluated if '
                '"``--missing``" is set to "include" or if "``--missing``" is '
                'set to "auto" (default) and the resolution is "problem"')
        info %= ', '.join(self.commonly_solved_foci)
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
            for problem in self.problems:
                if (problem.domain == run['domain'] and
                    problem.problem == run['problem']):
                    return True
            return False

        def filter_by_config(run):
            """
            If configs is set, only process those configs, otherwise process
            all configs
            """
            for config in self.configs:
                if config == run['config']:
                    return True
            return False

        if self.configs:
            self.add_filter(filter_by_config)
        if self.problems:
            self.add_filter(filter_by_problem)

        if self.filter:
            self.parse_filters()

    def name(self):
        name = Report.name(self)
        if self.configs:
            name += '-' + '+'.join(self.configs)
        if self.suite:
            name += '-' + '+'.join(self.suite)
        name += '-' + self.resolution[0]
        name += '-' + self.report_type
        return name

    def parse_filters(self):
        '''
        Filter strings have the form e.g.
        expanded:lt:100 or solved:eq:1 or generated:ge:2000
        '''
        for string in self.filter:
            self.parse_filter(string)

    def parse_filter(self, string):
        attribute, op, value = string.split(':')

        try:
            value = float(value)
        except ValueError:
            pass

        try:
            op = getattr(operator, op.lower())
        except AttributeError:
            logging.error('The operator module has no operator "%s"' % op)
            sys.exit()

        self.add_filter(lambda run: op(run[attribute], value))

    def get_configs(self):
        """
        Return the list of configs

        Either they have been set on the commandline, or we take all configs
        found in the runs
        """
        if self.configs:
            return self.configs
        return list(set([run['config'] for run in self.orig_data]))

    def _filter_common_attributes(self, focus):
        """
        for an attribute include or ignore problems for which not
        all configs have this attribute. --missing=auto includes those
        problems in the detailed view and ignores them in the
        domain-summary reports
        """
        # For some reports include all runs
        if (focus not in self.commonly_solved_foci or
                self.handle_missing_attrs == 'include' or
                (self.handle_missing_attrs == 'auto' and
                    self.resolution == 'problem')):
            return

        logging.info('Filtering problems with missing attributes for runs')
        for (domain, problem), group in self.data.group_dict('domain', 'problem').items():
            values = group[focus]

            any_missing = any(map(lambda value: value is missing, values))
            logging.debug('MISSING %s %s:%s %s, %s' %
                    (focus, domain, problem, group[focus], any_missing))
            if any_missing:
                def delete_runs_with_missing_attributes(run):
                    if run['domain'] == domain and run['problem'] == problem:
                        return False
                    return True

                self.data.filter(delete_runs_with_missing_attributes)

    def _get_table(self, focus):
        '''
        Returns an empty table. Used and filled by subclasses.
        '''
        self._filter_common_attributes(focus)

        # Decide on a group function
        if 'score' in focus:
            self.group_func = reports.avg
        elif focus in ['search_time', 'total_time']:
            self.group_func = reports.gm
        else:
            self.group_func = sum

        # Decide whether we want to highlight minima or maxima
        max_attributes = ['solved', 'score', 'initial_h_value', 'coverage']
        min_wins = True
        for attr_part in max_attributes:
            if attr_part in focus:
                min_wins = False
        table = PlanningTable(focus, min_wins=min_wins)
        return table


class AnyAttributeReport(PlanningReport):
    """
    Write an any-attribute (anytime, any-expanded, ...) report
    || time            | fF               | yY               |
    | 10               | 10               | 12               |
    | 20               | 21               | 17               |
    """
    def __init__(self, *args, **kwargs):
        PlanningReport.__init__(self, *args, **kwargs)

    def _get_table(self, focus):
        table = PlanningTable(focus, highlight=False, numeric_rows=True)

        if len(self.foci) != 1:
            logging.error("Please select exactly one attribute for an "
                          "any-attribute report")
            sys.exit(1)

        min_value = 0
        max_value = 1800
        step = 5

        self.set_grouping('config')
        for config, group in self.group_dict.items():
            group.filter(solved=1)
            group.sort(focus)
            for time_limit in xrange(min_value, max_value + step, step):
                table.add_cell(str(time_limit), config,
                    len(group.filtered(lambda di: di[focus] <= time_limit)))
        return table


class AbsolutePlanningReport(PlanningReport):
    """
    Write an absolute report about the focus attribute, e.g.

    || expanded        | fF               | yY               |
    | **gripper     ** | 118              | 72               |
    | **zenotravel  ** | 21               | 17               |
    """
    def __init__(self, *args, **kwargs):
        PlanningReport.__init__(self, *args, **kwargs)

    def _get_table(self, focus):
        table = PlanningReport._get_table(self, focus)
        func = self.group_func

        def show_missing_attribute_msg(name):
            msg = '%s: The attribute "%s" was not found. ' % (name, focus)
            logging.error(msg)

        if self.resolution == 'domain':
            self.set_grouping('config', 'domain')
            for (config, domain), group in self.group_dict.items():
                values = filter(lambda val: val is not missing, group[focus])
                if not values:
                    show_missing_attribute_msg(config + '-' + domain)
                    continue
                table.add_cell(domain, config, func(values))
        elif self.resolution == 'problem':
            self.set_grouping('config', 'domain', 'problem')
            for (config, domain, problem), group in self.group_dict.items():
                values = filter(lambda val: val is not missing, group[focus])
                name = domain + ':' + problem
                if not values:
                    show_missing_attribute_msg(name)
                    continue
                assert len(values) <= 1, \
                    '%s occurs in results more than once' % name
                table.add_cell(name, config, func(values))

        if self.resolution == 'suite' or not self.hide_sum_row:
            self.set_grouping('config')

            if self.resolution == 'suite':
                row_name = '-'.join(self.suite) if self.suite else 'Suite'
            else:
                row_name = func.__name__.upper()
            for config, group in self.group_dict.items():
                values = filter(lambda val: val is not missing, group[focus])
                if not values:
                    show_missing_attribute_msg(config)
                    continue
                table.add_cell(row_name, config, func(values))
        return table


class ComparativePlanningReport(PlanningReport):
    """
    Write a comparative report about the focus attribute, e.g.

    ||                               | fF/yY            |
    | **grid**                       | 0 - 1 - 0        |
    | **gripper**                    | 0 - 0 - 3        |
    | **zenotravel**                 | 0 - 1 - 1        |
    """
    def __init__(self, *args, **kwargs):
        PlanningReport.__init__(self, *args, **kwargs)

    def _get_table(self, focus):
        table = PlanningReport._get_table(self, focus)

        if self.resolution == 'domain':
            self.set_grouping('domain')
            for domain, group in self.group_dict.items():
                values = Table()
                config_prob_to_group = group.group_dict('config', 'problem')
                for (config, problem), subgroup in config_prob_to_group.items():
                    vals = subgroup[focus]
                    assert len(vals) == 1
                    val = vals[0]
                    values.add_cell(problem, config, val)
                (config1, config2), sums = values.get_comparison()
                table.add_cell(domain, config1 + '/' + config2,
                                        '%d - %d - %d' % tuple(sums))
        elif self.resolution == 'problem':
            logging.error('Comparative reports only make sense for domains and suites')
            sys.exit(1)

        if self.resolution == 'suite' or not self.hide_sum_row:
            if self.resolution == 'suite':
                row_name = '-'.join(self.suite) if self.suite else 'Suite'
            else:
                row_name = 'SUM'
            self.set_grouping()
            for group in self.group_dict.values():
                values = Table()
                config_prob_to_group = group.group_dict('config', 'domain', 'problem')
                for (config, domain, problem), subgroup in config_prob_to_group.items():
                    vals = subgroup[focus]
                    assert len(vals) == 1
                    val = vals[0]
                    values.add_cell(domain + ':' + problem, config, val)
                (config1, config2), sums = values.get_comparison()
                table.add_cell(row_name, config1 + '/' + config2,
                               '%d - %d - %d' % tuple(sums))
        return table


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

        self.resolution = 'problem'
        self.set_grouping(None)

    def write(self):
        self.data = self.orig_data.copy()
        data = self.data.filtered(*self.filter_funcs, **self.filter_pairs)
        if len(data) == 0:
            sys.exit('No problems match those filters')
        problems = [run['domain'] + ':' + run['problem'] for run in data]
        # Sort and remove duplicates
        problems = sorted(set(problems))
        problems = ['        "%s",\n' % problem for problem in problems]
        self.output = ('def suite():\n    return [\n%s    ]\n' %
                       ''.join(problems))
        print '\nSUITE:'
        print self.output

        if not self.dry:
            exp_name = os.path.basename(self.eval_dir).replace('-eval', '')
            filters = '_'.join(self.filter)
            filters = filters.replace(':', '')
            parts = [exp_name, 'suite']
            if filters:
                parts.append(filters)
            filename = '_'.join(parts) + '.py'
            output_file = os.path.join(self.report_dir, filename)
            with open(output_file, 'w') as file:
                output_uri = 'file://' + os.path.abspath(output_file)
                logging.info('Writing output to %s' % output_uri)
                file.write(self.output)

        logging.info('Finished writing report')


if __name__ == "__main__":
    known_args, remaining_args = report_type_parser.parse_known_args()

    # delete parsed args
    sys.argv = [sys.argv[0]] + remaining_args

    report_type = known_args.report
    logging.info('Report type: %s' % report_type)

    if report_type == 'abs':
        report = AbsolutePlanningReport()
    elif report_type == 'cmp':
        report = ComparativePlanningReport()
    elif report_type == 'any':
        report = AnyAttributeReport()
    elif report_type == 'suite':
        report = SuiteReport()

    # Copy the report type
    report.report_type = report_type

    report.write()
    report.open()

    #report.add_filter(domain='gripper')
    #report.add_filter(lambda item: item['expanded'] == '21')
    #report.add_filter(lambda item: item['expanded'] < 10)
