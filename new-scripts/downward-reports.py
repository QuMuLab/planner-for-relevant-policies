#! /usr/bin/env python
"""
Module that permits generating downward reports by reading properties files
"""

from __future__ import with_statement, division

import sys
import os
import logging
import datetime

import tools
import planning_suites
from external import datasets
from markup import Document
from reports import Report, ReportArgParser, Table


# Create a parser only for parsing the report type
report_type_parser = tools.ArgParser(add_help=False)
report_type_parser.epilog = 'Note: The help output may depend on the already selected options'
report_type_parser.add_argument('-r', '--report', choices=['abs', 'rel', 'cmp'],
                                default='abs', help='Select a report type')



class PlanningReport(Report):
    """
    """
    def __init__(self, parser=ReportArgParser(parents=[report_type_parser])):
        parser.add_argument('-c', '--configs', nargs='*', default=[], 
            help='planner configurations (if none specified, use all found configs)')
        parser.add_argument('-s', '--suite', nargs='*', default=[], 
            help='tasks, domains or suites (if none specified, use whole suite)')
        parser.add_argument('--res', default='domain', dest='resolution',
            help='resolution of the report', choices=['suite', 'domain', 'problem'])
        
        Report.__init__(self, parser)
        
        self.focus = None
        self.output = ''
        
        self.problems = planning_suites.build_suite(self.suite)
        
        def filter_by_problem(run):
            """
            If suite is set, only process problems from the suite, 
            otherwise process all problems
            """
            if not self.problems:
                return True
            for problem in self.problems:
                if problem.domain == run['domain'] and problem.problem == run['problem']:
                    return True
            return False
            
        def filter_by_config(run):
            """
            If configs is set, only process those configs, otherwise process all configs
            """
            if not self.configs:
                return True
            for config in self.configs:
                if config == run['config']:
                    return True
            return False
        
        self.add_filter(filter_by_problem, filter_by_config)
            
            
    def name(self):
        name = Report.name(self)
        if self.configs:
            name += '-' + '+'.join(self.configs)
        if self.suite:
            name += '-' + '+'.join(self.suite)
        name += '-' + self.resolution[0]
        name += '-' + self.report
        return name
        
        
    def _get_table(self):
        '''
        Returns an empty table. Used and filled by subclasses.
        '''
        max_attributes = ['solved', 'score']
        min_wins = True
        for attr in max_attributes:
            if attr in self.focus:
                min_wins = False
        table = Table(self.focus, min_wins=min_wins)
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
            
            
    def _get_table(self):
        func = self.group_func
        table = PlanningReport._get_table(self)
        
        def existing(val):
            return not type(val) == datasets.MissingType
            
        def show_missing_attribute_msg():
            msg = 'No data has the attribute "%s". ' % self.focus
            msg += 'Are you sure you typed it in correctly?'
            logging.error(msg)
        
        
        if self.resolution == 'domain':
            self.set_grouping('config', 'domain')
            for (config, domain), group in self.group_dict.items():
                values = filter(existing, group[self.focus])
                if not values:
                    show_missing_attribute_msg()
                table.add_cell(domain, config, func(values))
        elif self.resolution == 'problem':
            self.set_grouping('config', 'domain', 'problem')
            for (config, domain, problem), group in self.group_dict.items():
                values = filter(existing, group[self.focus])
                if not values:
                    show_missing_attribute_msg()
                table.add_cell(domain + ':' + problem, config, func(values))
        
        if self.resolution == 'suite' or not self.hide_sum_row:
            self.set_grouping('config')
            
            if self.resolution == 'suite':
                row_name = '-'.join(self.suite) if self.suite else 'Suite'
            else:
                row_name = 'SUM'
            for (config,), group in self.group_dict.items():
                values = filter(existing, group[self.focus])
                if not values:
                    show_missing_attribute_msg()
                table.add_cell(row_name, config, func(values))
            
        return table
        
        
        
class RelativePlanningReport(AbsolutePlanningReport):
    """
    Write a relative report about the focus attribute, e.g.
    
    || expanded        | fF               | yY               |
    | **gripper     ** | 1.0              | 0.6102           |
    | **zenotravel  ** | 1.0              | 0.8095           |
    """
    def __init__(self, *args, **kwargs):
        AbsolutePlanningReport.__init__(self, *args, **kwargs)
        
    
    def _get_table(self):        
        absolute_table = AbsolutePlanningReport._get_table(self)
        table = absolute_table.get_relative()
        
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
        
    
    def _get_table(self):
        table = PlanningReport._get_table(self)
        
        if self.resolution == 'domain':
            self.set_grouping('domain')
            for (domain,), group in self.group_dict.items():
                values = Table()
                config_prob_to_group = group.group_dict('config', 'problem')
                for (config, problem), subgroup in config_prob_to_group.items():
                    vals = subgroup[self.focus]
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
            for _, group in self.group_dict.items():
                values = Table()
                config_prob_to_group = group.group_dict('config', 'domain', 'problem')
                for (config, domain, problem), subgroup in config_prob_to_group.items():
                    vals = subgroup[self.focus]
                    assert len(vals) == 1
                    val = vals[0]
                    values.add_cell(domain + ':' + problem, config, val)
                (config1, config2), sums = values.get_comparison()
                table.add_cell(row_name, config1 + '/' + config2, 
                                        '%d - %d - %d' % tuple(sums))
            
        return table
        
        
if __name__ == "__main__":
    known_args, remaining_args = report_type_parser.parse_known_args()
    
    # delete parsed args
    sys.argv = [sys.argv[0]] + remaining_args
    
    report_type = known_args.report
    logging.info('Report type: %s' % report_type)
    
    if report_type == 'abs':
        report = AbsolutePlanningReport()
    elif report_type == 'rel':
        report = RelativePlanningReport()
    elif report_type == 'cmp':
        report = ComparativePlanningReport()
        
    report.build()
    print report
    report.write()
        
    #report.add_filter(domain='gripper')
    #report.add_filter(lambda item: item['expanded'] == '21')
    #report.set_grouping('config', 'domain', 'problem')
    #report.write()
    #print report_text
