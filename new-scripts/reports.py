#! /usr/bin/env python
'''
Module that permits generating reports by reading properties files
'''

from __future__ import with_statement

import os
import sys
import shutil
import re
from optparse import OptionParser
from glob import glob
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(levelname)-8s %(message)s',)
                    
import tools
from external.configobj import ConfigObj
from external.datasets import DataSet
      
      

class ReportOptionParser(OptionParser):
    def __init__(self, *args, **kwargs):
        OptionParser.__init__(self, option_class=tools.ExtOption, *args, **kwargs)
        
        self.add_option(
            "-s", "--source", action="store", dest="eval_dir", default="",
            help="path to evaluation directory")
        self.add_option(
            "-d", "--dest", action="store", dest="report_dir", default="",
            help="path to report directory (default: <eval_dir>-report)")
            
        self.add_option(
            "-r", "--run-filter", action="extend", dest="run_filter", default=[],
            help="")
        
    def error(self, msg):
        '''Show the complete help AND the error message'''
        self.print_help()
        OptionParser.error(self, msg)
        
    def parse_options(self):
        options, args = self.parse_args()
        
        if not options.eval_dir:
            raise self.error('You need to specify an evaluation directory')
        options.eval_dir = os.path.normpath(os.path.abspath(options.eval_dir))
        logging.info('Eval dir:  "%s"' % options.eval_dir)
        if not os.path.isdir(options.eval_dir):
            raise self.error('"%s" is no directory' % options.eval_dir)
        
        if not options.report_dir:
            parent_dir = os.path.dirname(options.eval_dir)
            dir_name = os.path.basename(options.eval_dir)
            options.report_dir = os.path.join(parent_dir, dir_name + '-report')
            logging.info('Report dir: "%s"' % options.report_dir)
            
        options.run_filter = []
        
        return options
        
    

class Report(object):
    '''
    Base class for all reports
    '''
    
    def __init__(self, parser=ReportOptionParser()):
        self.parser = parser
        options = self.parser.parse_options()
        # Give all the options to the report instance
        self.__dict__.update(options.__dict__)
        
        self.data = self._get_data()
        
        self.filter_funcs = []
        self.filter_pairs = {}
        
        self.grouping = None
        self.order = None
        
    def add_run_filter(self, *filter_funcs, **filter_pairs):
        self.filter_funcs.extend(filter_funcs)
        self.filter_pairs.update(filter_pairs)
        
    def set_grouping(self, *grouping):
        self.grouping = grouping
        
    def set_order(self, *order):
        self.order = order
        
    def build(self):
        #raise Exception('Not Implemented')
        data = DataSet(self.data)
        data.dump()
        
        if not self.order:
            self.order = ['expanded']
        data.sort(*self.order)
        print 'SORTED'
        data.dump()
        
        if self.filter_funcs or self.filter_pairs:
            data = data.filtered(*self.filter_funcs, **self.filter_pairs)
            print 'FILTERED'
            data.dump()
        if self.grouping:
            groups = data.groups(*self.grouping)
            print 'GROUPED'
            for name, group in groups:
                print group
        
        
    def _get_data(self):
        data = DataSet()
        for base, dir, files in os.walk(self.eval_dir):
            for file in files:
                if file == 'properties':
                    file = os.path.join(base, file)
                    print 'FILE', open(file).read()
                    props = tools.Properties(file)
                    print props
                    print
                    data.append(**props)
        return data
    


if __name__ == "__main__":
    if len(sys.argv) == 1:
        sys.argv.extend(['-s', 'test-eval'])
    report = Report()
    report.add_run_filter(domain='gripper')
    #report.add_run_filter(lambda item: item['expanded'] == '21')
    report.set_grouping('domain', 'config')
    data = report.data
    print 'ITEMS', data.items
    #for _, group in data.groups('config', 'domain'):
    #    group.dump()
    #print
    #for item in data.filtered(config='yY'):
    #    print item
    
    report.build()
    

