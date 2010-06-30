#! /usr/bin/env python
'''
Module that permits evaluating experiments conducted with experiments.py
'''

from __future__ import with_statement

import os
import sys
import shutil
from optparse import OptionParser
from glob import glob
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)8s %(message)s',)
                    
import tools
from external.configobj import ConfigObj
      
      

class EvalOptionParser(OptionParser):
    def __init__(self, *args, **kwargs):
        OptionParser.__init__(self, option_class=tools.ExtOption, *args, **kwargs)
        
        self.add_option(
            "-s", "--source", action="store", dest="exp_dir", default="",
            help="path to experiment directory")
        self.add_option(
            "-d", "--dest", action="store", dest="eval_dir", default="",
            help="path to evaluation directory (default: <exp_dir>-eval)")
        
    def error(self, msg):
        '''Show the complete help AND the error message'''
        self.print_help()
        OptionParser.error(self, msg)
        
    def parse_options(self):
        options, args = self.parse_args()
        
        if not options.exp_dir:
            raise self.error('You need to specify an experiment directory')
        options.exp_dir = os.path.normpath(os.path.abspath(options.exp_dir))
        logging.info('Exp dir:  "%s"' % options.exp_dir)
        if not os.path.isdir(options.exp_dir):
            raise self.error('"%s" is no directory' % options.exp_dir)
        
        if not options.eval_dir:
            parent_dir = os.path.dirname(options.exp_dir)
            dir_name = os.path.basename(options.exp_dir)
            options.eval_dir = os.path.join(parent_dir, dir_name + '-eval')
            logging.info('Eval dir: "%s"' % options.eval_dir)
        
        return options
        


    

class Evaluation(object):
    '''
    Base class for all evaluations
    '''
    
    def __init__(self, parser=EvalOptionParser()):
        self.parser = parser
        options = self.parser.parse_options()
        # Give all the options to the experiment instance
        self.__dict__.update(options.__dict__)
        
    def evaluate(self):
        raise Exception('Not Implemented')
        
        
class CopyEvaluation(Evaluation):
    '''
    Simple evaluation that copies files from run dirs into a new tree under
    <eval-dir> according to the value "id" in the run's properties file
    '''
    def __init__(self, *args, **kwargs):
        Evaluation.__init__(self, *args, **kwargs)
        
    def evaluate(self):
        copy_dict = {}
        
        run_dirs = self._get_run_dirs()
        for run_dir in run_dirs:
            prop_file = os.path.join(run_dir, 'properties')
            props = ConfigObj(prop_file)
            id = props.get('id')
            dest = os.path.join(self.eval_dir, *id)
            copy_dict[run_dir] = dest
            
        for source, dest in copy_dict.items():
            tools.updatetree(source, dest)
        
    def _get_run_dirs(self):
        run_dirs = glob(os.path.join(self.exp_dir, 'runs-*-*', '*'))
        return run_dirs
        
        
def build_evaluator(parser=EvalOptionParser()):
    eval = CopyEvaluation(parser)
    return eval


if __name__ == "__main__":
    eval = build_evaluator()
    eval.evaluate()
    
