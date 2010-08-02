#! /usr/bin/env python
"""
Module that permits generating reports by reading properties files
"""

from __future__ import with_statement, division

import os
import sys
import shutil
import re
from glob import glob
from collections import defaultdict
from itertools import combinations
import logging
import datetime
import collections
import operator
import cPickle

logging.basicConfig(level=logging.INFO, format='%(relativeCreated)-s %(levelname)-8s %(message)s',)
                    
import tools
import planning_suites
from markup import Document
from external.configobj import ConfigObj
from external.datasets import DataSet
from external import datasets
from external import txt2tags
from external import argparse



# Create a parser only for parsing the report type
report_type_parser = tools.ArgParser(add_help=False)
report_type_parser.add_argument('--report', choices=['abs', 'rel', 'cmp'],
                                default='abs', help='Select a report type')


class ReportArgParser(tools.ArgParser):
    def __init__(self, *args, **kwargs):
        tools.ArgParser.__init__(self, *args, parents=[report_type_parser], **kwargs)
        
        self.epilog = 'Note: The help output depends on the selected report type'
      
        self.add_argument('source', help='path to evaluation directory', 
                            type=self.directory)
        
        self.add_argument('-d', '--dest', dest='report_dir', default='reports',
                            help='path to report directory')
                        
        self.add_argument('--format', dest='output_format', default='tex',
                            help='format of the output file',
                            choices=sorted(txt2tags.TARGETS))
                            
        self.add_argument('focus', 
                            help='the analyzed attribute (e.g. "expanded")')
                            
        self.add_argument('--group-func', default='sum',
                        help='the function used to cumulate the values of a group')
                        
        self.add_argument('--hide-sum', dest='hide_sum_row',
                        default=False, action='store_true',
                        help='do not add a row that sums up each column')
                        
        self.add_argument('--dry', default=False, action='store_true',
                        help='do not write anything to the filesystem')
                        
        self.add_argument('--reload', default=False, action='store_true',
                        help='rescan the directory and reload the properties files')
                        
        self.add_argument('-a', '--attributes', dest='show_attributes',
                        default=False, action='store_true',
                        help='show a list of available attributes and exit')
                        
                        
    def parse_args(self, *args, **kwargs):
        args = argparse.ArgumentParser.parse_args(self, *args, **kwargs)
        args.eval_dir = args.source
        
        args.eval_dir = os.path.normpath(os.path.abspath(args.eval_dir))
        logging.info('Eval dir: "%s"' % args.eval_dir)
        
        if not os.path.exists(args.report_dir):
            os.makedirs(args.report_dir)
            
        # Turn e.g. the string 'max' into the function max()
        args.group_func = eval(args.group_func)
        
        #if not args.report_dir:
        #    parent_dir = os.path.dirname(args.eval_dir)
        #    dir_name = os.path.basename(args.eval_dir)
        #    args.report_dir = os.path.join(parent_dir, dir_name + '-report')
        #    logging.info('Report dir: "%s"' % args.report_dir)
        
        return args
        
    

class Report(object):
    """
    Base class for all reports
    """
    
    def __init__(self, parser=ReportArgParser()):
        # Give all the options to the report instance
        parser.parse_args(namespace=self)
        
        self.data = self._get_data()
        
        if self.show_attributes:
            print
            print 'Available attributes:'
            print self.data.get_attributes()
            sys.exit()
        
        self.filter_funcs = []
        self.filter_pairs = {}
        
        self.grouping = []
        self.order = []

        
    def set_focus(self, attribute):
        """
        Define which attribute the report should be about
        """
        self.focus = attribute
        
        
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
        
       
    @property
    def group_dict(self):
        data = DataSet(self.data)
        
        if not self.order:
            self.order = ['id']
        data.sort(*self.order)
        #print 'SORTED'
        #data.dump()
        
        if self.filter_funcs or self.filter_pairs:
            data = data.filtered(*self.filter_funcs, **self.filter_pairs)
            #print 'FILTERED'
            #data.dump()
        
        group_dict = data.group_dict(*self.grouping)
        #print 'GROUPED'
        #print group_dict
                
        return group_dict
        
        
    def _get_data(self):
        dump_path = os.path.join(self.eval_dir, 'data_dump')
        
        dump_exists = os.path.exists(dump_path)
        if self.reload or not dump_exists:
            data = DataSet()
            logging.info('Started collecting data')
            for base, dir, files in os.walk(self.eval_dir):
                for file in files:
                    if file == 'properties':
                        file = os.path.join(base, file)
                        props = tools.Properties(file)
                        data.append(**props)
            # Pickle data for faster future use
            cPickle.dump(data, open(dump_path, 'w'))
            logging.info('Wrote data dump')
            logging.info('Finished collecting data')
        else:
            data = cPickle.load(open(dump_path))
        return data
                            
        

class Table(collections.defaultdict):
    def __init__(self, title='', sum=True):
        collections.defaultdict.__init__(self, dict)
        
        self.title = title
        self.sum = sum
        
        
    def add_cell(self, row, col, value):
        self[row][col] = value
        
        
    @property    
    def rows(self):
        rows = self.keys()
        # Let the sum row be the last one
        key = lambda row: 'zzz' if row.upper() == 'SUM' else row.lower()
        rows = sorted(rows, key=key)
        return rows
        
        
    @property
    def cols(self):
        cols = []
        for dict in self.values():
            for key in dict.keys():
                if key not in cols:
                    cols.append(key)
        return sorted(cols)
        
        
    def get_cells_in_row(self, row):
        return self[row].values()
        
        
    def get_sum_row(self):
        """
        Unused
        """
        sums = defaultdict(int)
        for row in self.rows:
            for col, value in self[row].items():
                sums[col] += value
        text += '| %-30s ' % '**Sum**'
        for col, sum in sorted(sums.items()):
            text += '| %-16s ' % ('**'+str(sum)+'**')
        text += '|\n'
        return text
        
        
    def get_relative(self):
        """
        Find the max in each row and write the relative value into each cell.
        Returns a new table
        """
        rel_table = Table(self.title)
        for row in self.rows:
            max_in_row = max(self[row].values())
            for col, cell in self[row].items():
                rel_value = 0 if max_in_row == 0 else round(cell / max_in_row, 4)
                rel_table.add_cell(row, col, rel_value)
        return rel_table
        
        
    def get_comparison(self, comparator=cmp):
        """
        || expanded                      | fF               | yY               |
        | **prob01.pddl**                | 21               | 16               |
        | **prob02.pddl**                | 38               | 24               |
        | **prob03.pddl**                | 59               | 32               |
        ==>
        returns ((fF, yY), (0, 0, 3)) [wins, draws, losses]
        """
        assert len(self.cols) == 2, 'For comparative reports please specify 2 configs'
        
        sums = [0, 0, 0]
        
        for row in self.rows:
            for col1, col2 in combinations(self.cols, 2):
                val1 = self[row][col1]
                val2 = self[row][col2]
                cmp_value = comparator(val1, val2)
                sums[cmp_value + 1] += 1
                    
        return (self.cols, sums)
        
        
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
        
        text += ' | '.join(map(lambda col: '%-16s' % col, cols)) + ' |\n'
        for row in rows:
            text += '| %-30s ' % ('**'+row+'**')
            for col in cols:
                text += '| %-16s ' % self.get(row).get(col)
            text += '|\n'
        return text
        
        
        
class PlanningReport(Report):
    """
    """
    def __init__(self, parser=ReportArgParser()):
        parser.add_argument('-c', '--configs', nargs='*',
                            default=[], help="planner configurations")
            
        parser.add_argument('-s', '--suite', nargs='*',
                            default=[], help='tasks, domains or suites')
            
        parser.add_argument('-r', '--resolution', default='domain',
                            choices=['suite', 'domain', 'problem'])
        Report.__init__(self, parser)
        
        self.output = ''
        self.compared_attribute = 'config'
        
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
            
            
    @property
    def name(self):
        eval_dir = os.path.basename(self.eval_dir)
        configs = self.configs or ['*']
        suite = self.suite or ['*']
        parts = [[eval_dir], configs, suite, [self.resolution], [self.focus]]
        return '_'.join(['-'.join(vars) for vars in parts])
        
    
    def get_table(self):
        raise Error('Not implemented')
        
        
    def build(self):
        table = self.get_table()
        print table
        
        doc = Document(title=self.name)
        doc.add_text(str(table))
        
        self.output = doc.render(self.output_format)
        #print 'OUTPUT:'
        #print self.output
        return self.output
        
        
    def write(self):
        if not self.output:
            self.output = self.build()
            
        if not self.dry:
            output_file = os.path.join(self.report_dir, 
                self.name + '.' + self.output_format)
            with open(output_file, 'w') as file:
                logging.info('Writing output to "%s"' % output_file)
                file.write(self.output)
        
        logging.info('Finished writing report')
        



class AbsolutePlanningReport(PlanningReport):
    """
    Write an absolute report about the focus attribute, e.g.
    
    || expanded        | fF               | yY               |
    | **gripper     ** | 118              | 72               |
    | **zenotravel  ** | 21               | 17               |
    """
    def __init__(self, *args, **kwargs):
        PlanningReport.__init__(self, *args, **kwargs)
            
            
    @property
    def name(self):
        return PlanningReport.name.fget(self) + '_abs'
        
    
    def get_table(self):
        func = self.group_func
        
        table = Table(self.focus)
        
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
            row_name = '-'.join(self.suite) if self.resolution == 'suite' else 'SUM'
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
        
    
    @property
    def name(self):
        return PlanningReport.name.fget(self) + '_rel'
                
    
    def get_table(self):
        func = self.group_func
        
        absolute_table = AbsolutePlanningReport.get_table(self)
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
        
        self.compared_attribute = 'config'
            
    
    @property
    def name(self):
        return PlanningReport.name.fget(self) + '_cmp'
        
    
    def get_table(self):
        
        
        func = self.group_func
        
        table = Table(self.focus)
        
        
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
            row_name = '-'.join(self.suite) if self.resolution == 'suite' else 'SUM'
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
    #if len(sys.argv) == 1:
    #    sys.argv.extend('test-eval expanded -s MINITEST -c yY fF --resolution domain'.split())
    known_args, remaining_args = report_type_parser.parse_known_args()
    report_type = known_args.report
    logging.info('Report type: %s' % report_type)
    
    if report_type == 'abs':
        report = AbsolutePlanningReport()
    elif report_type == 'rel':
        report = RelativePlanningReport()
    elif report_type == 'cmp':
        report = ComparativePlanningReport()
        
    #report.add_filter(domain='gripper')
    #report.add_filter(lambda item: item['expanded'] == '21')
    #report.set_grouping('config', 'domain', 'problem')
    report.write()
    

