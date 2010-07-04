#! /usr/bin/env python
'''
Module that permits evaluating experiments conducted with experiments.py
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
      
      

class ReportOptionParser(OptionParser):
    def __init__(self, *args, **kwargs):
        OptionParser.__init__(self, option_class=tools.ExtOption, *args, **kwargs)
        
        self.add_option(
            "-s", "--source", action="store", dest="eval_dir", default="",
            help="path to evaluation directory")
        self.add_option(
            "-d", "--dest", action="store", dest="report_dir", default="",
            help="path to report directory (default: <eval_dir>-report)")
        
    def error(self, msg):
        '''Show the complete help AND the error message'''
        self.print_help()
        OptionParser.error(self, msg)
        
    def parse_options(self):
        options, args = self.parse_args()
        
        if not options.eval_dir:
            raise self.error('You need to specify an experiment directory')
        options.eval_dir = os.path.normpath(os.path.abspath(options.eval_dir))
        logging.info('Eval dir:  "%s"' % options.eval_dir)
        if not os.path.isdir(options.eval_dir):
            raise self.error('"%s" is no directory' % options.eval_dir)
        
        if not options.report_dir:
            parent_dir = os.path.dirname(options.eval_dir)
            dir_name = os.path.basename(options.eval_dir)
            options.report_dir = os.path.join(parent_dir, dir_name + '-report')
            logging.info('Report dir: "%s"' % options.report_dir)
        
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
        
    def build(self):
        raise Exception('Not Implemented')
        
    def _get_prop_files(self):
        prop_files = []
        for base, dir, files in os.walk(self.eval_dir):
            for file in files:
                print file
        return prop_files
    
    
        
#def build_report(parser=ReportOptionParser()):
#    report = Report(parser)
#    return report


if __name__ == "__main__":
    report = Report()
    report._get_prop_files()
    report.build()
    

