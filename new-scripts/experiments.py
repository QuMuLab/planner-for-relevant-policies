#! /usr/bin/env python

from __future__ import with_statement

import os
import sys
import shutil
from optparse import OptionParser, OptionValueError
import logging
import math

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)8s %(message)s',)


def divide_list(seq, size):
    '''
    >>> divide_list(range(10), 4)
    [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]
    '''
    return [seq[i:i+size] for i  in range(0, len(seq), size)]

def overwrite_dir(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.mkdir(dir)
    
    

class Experiment(object):
    
    def __init__(self, options):
        # Give all the options to the experiment instance
        self.__dict__.update(options.__dict__)
        
        self.runs = []
        
        self.base_dir = os.path.join(self.exp_root_dir, self.exp_name)
        self.resources = []
        
    def add_resource(self, resource_name, source, dest):
        '''
        Example:
        >>> experiment.add_resource("PLANNER", "../downward/search/release-search",
                                    "release-search")
                                    
        Includes a "global" file, i.e., one needed for all runs, into the
        experiment archive. In case of GkiGridExperiment, copies it to the
        main directory of the experiment. The name "PLANNER" is an ID for
        this resource that can also be used to refer to it in shell scripts.
        '''
        self.resources.append((resource_name, source, dest))
        
    def add_run(self, run=None):
        '''
        Factory for Runs
        Schedule this run to be part of the experiment.
        '''
        run = Run(self)
        self.runs.append(run)
        return run
        
    def build(self):
        '''
        Apply all the actions to the filesystem
        '''
        overwrite_dir(self.base_dir)
        
        self._set_run_dirs()
        self._build_main_script()
        self._build_runs()
        

    def _set_run_dirs(self):
        '''
        Sets the relative run directories as instance 
        variables for all runs
        '''
        def get_run_number(number):
            return str(number).zfill(5)
        
        def get_shard_dir(shard_number):
            first_run = self.shard_size * (shard_number - 1) + 1
            last_run = self.shard_size * (shard_number)
            return 'runs-%s-%s' % (get_run_number(first_run), get_run_number(last_run))
           
        current_run = 0
        
        shards = divide_list(self.runs, self.shard_size)
        
        for shard_number, shard in enumerate(shards, start=1):
            shard_dir = os.path.join(self.base_dir, get_shard_dir(shard_number))
            overwrite_dir(shard_dir)
            
            for run in shard:
                current_run += 1
                rel_dir = os.path.join(get_shard_dir(shard_number), get_run_number(current_run))
                run.rel_dir = rel_dir
        
        
    def _build_main_script(self):
        '''
        Generates the main script
        '''
        if self.exp_type == 'gkigrid':
            num_tasks = math.ceil(len(self.runs) / float(self.runs_per_task))
            job_params = {
                "logfile": self.exp_name + ".log",
                "errfile": self.exp_name + ".err",
                "driver_timeout": self.timeout + 30,
                "num_tasks": num_tasks,
            }
            script_template = open('data/gkigrid-job-header-template').read()
            script = script_template % job_params
            
            script += '\n'
            
            run_groups = divide_list(self.runs, self.runs_per_task)
            
            for task_id, run_group in enumerate(run_groups, start=1):
                script += 'if [[ $SGE_TASK_ID == %s ]]; then\n' % task_id
                for run in run_group:
                    # Here we need the relative directory
                    script += '  ./%s/invoke\n' % run.rel_dir
                script += 'fi\n'
                            
            
            name = self.exp_name
            filename = name if name.endswith('.q') else name + '.q'
            filename = os.path.join(self.base_dir, filename)
            
            with open(filename, 'w') as file:
                file.write(script)
                
                
    def _build_runs(self):
        '''
        Uses the relative directory information and writes all runs to disc
        '''
        for run in self.runs:
            run.build()



    


class Run(object):
    '''
    A Task can consist of one or multiple Runs
    '''
    
    def __init__(self, experiment):
        self.experiment = experiment
        
        # Save the directory relative to the main directory
        self.rel_dir = ''
        
        self.resources = []
        self.env_vars = []
        self.new_files = []
        
        self.command = ''
        self.preprocess_command = ''
        self.postprocess_command = ''
        
        self.add_resource('', 'data/gkigrid-invoke-template', 'invoke')
        
    #def require_resource(self, resource_name):
    #    '''
    #    Example:
    #    >>> run.require_resource("PLANNER")
    #    
    #    Make the planner resource available for this task.variable
    #    In environments like the argo cluster, this implies
    #    copying the planner into each task. For the gkigrid, we merely
    #    need to set up the PLANNER environment variable.
    #    '''
    
    # TODO: Discuss:
    # The require_resource method should be redundant.
    # We can use experiment.add_resource instead.
        
        
    def add_resource(self, resource_name, source, dest):
        '''
        Example:
        >>> run.add_resource("DOMAIN", "../benchmarks/gripper/domain.pddl",
                                "domain.pddl")
                                
        Copy "../benchmarks/gripper/domain.pddl" into the run
        directory under name "domain.pddl" and make it available as
        resource "DOMAIN" (usable as environment variable $DOMAIN).
        '''
        self.resources.append((source, dest))
        if resource_name:
            self.env_vars.append((resource_name, dest))
        
        
    def set_command(self, command):
        '''
        Example:
        run.set_command("$PLANNER %s <$INFILE" % options)
        
        A bash fragment that gives the code to be run when invoking
        this job.
        Optionally, can use run.set_preprocess() and
        run.set_postprocess() to specify code that should be run
        before the main command, i.e., outside the part for which we
        restrict runtime and memory. For example, post-processing
        could be used to rename result files or zipping them up. The
        postprocessing code should have some way of finding out
        whether the command succeeded or was aborted, e.g. via some
        environment variable.
        '''
        self.command = command
        
    def set_preprocess(self, preprocess_command):
        self.preprocess_command = preprocess_command
        
    def set_postprocess(self, postprocess_command):
        self.postprocess_command = postprocess_command
        
        
    def declare_optional_output(self, file_glob):
        '''
        Example:
        run.declare_optional_output("plan.soln*")
        
        Specifies that all files names "plan.soln*" (using
        shell-style glob patterns) are part of the experiment output.
        '''
        #TODO: Implement
        
        
    def declare_required_output(self, file_glob):
        '''
        There's a corresponding declare_required_output for output
        files that must be present at the end or we have an error. A
        specification like this is e.g. necessary for the Argo
        cluster. On the gkigrid, this wouldn't do anything, although
        the declared outputs should be stored somewhere so that we
        can later verify that all went according to plan.
        '''
        #TODO: Implement
        
        
    def build(self):
        '''
        After having made all the necessary adjustments with the methods above,
        this method can be used to write everything to the disk. 
        '''
        assert self.rel_dir
        
        # Make the directory relative to the directory of this script
        self.dir = os.path.join(self.experiment.base_dir, self.rel_dir)
        
        overwrite_dir(self.dir)
        self._build_run_script()
        self._build_resources()
             
            
    def _build_run_script(self):
        if not self.command:
            raise SystemExit('You have to specify a command via run.set_command()')
            
        if self.env_vars:
            env_vars_text = ''
            for var, filename in self.env_vars:
                env_vars_text += 'os.environ["%s"] = "%s"\n' % (var, filename)
        else:
            env_vars_text = '"Here you would find the declaration of envirionment variables"'
            
        run_script = open('data/gkigrid-run-template.py').read()
        replacements = {'ENVIRONMENT_VARIABLES': env_vars_text,
                        'RUN_COMMAND' :self.command,
                        'PREPROCESS_COMMAND': self.preprocess_command,
                        'POSTPROCESS_COMMAND': self.postprocess_command,
                        'TIMEOUT': str(self.experiment.timeout),
                        'MEMORY': str(self.experiment.memory),
                        }
        for orig, new in replacements.items():
            run_script = run_script.replace('***'+orig+'***', new)
        
        self.new_files.append(('run', run_script))
        
        
    def _build_resources(self):
        for name, content in self.new_files:
            filename = os.path.join(self.dir, name)
            with open(filename, 'w') as file:
                logging.info('Writing file "%s"' % filename)
                file.write(content)
                if name == 'run':
                    # Make run script executable
                    os.chmod(filename, 0755)
                    
                
        for source, dest in self.resources:
            dest = os.path.join(self.dir, dest)
            logging.info('Copying %s to %s' % (source, dest))
            try:
                shutil.copy2(source, dest)
            except IOError, err:
                raise SystemExit('Error: The file "%s" could not be copied to "%s": %s' % \
                                (source, dest, err))
        
        
        

def parse_options():
    #TODO: Let other modules inherit from this Parser to add their own commandline arguments
    
    def parse_comma_list(option, opt, value, parser):
      setattr(parser.values, option.dest, value.split(','))
      
    class ExpOptionParser(OptionParser):
        def error(self, msg):
            '''Show the complete help AND the error message'''
            self.print_help()
            OptionParser.error(self, msg)
      
    exp_types = ['gkigrid']#, 'local']

    parser = ExpOptionParser("usage: %prog [options]")
    
    parser.add_option(
        "--type", action="store", dest="exp_type", default="",
        help="type of the experiment (allowed values: %s)" % exp_types)
    parser.add_option(
        "-n", "--name", action="store", dest="exp_name", default="",
        help="name of the experiment (e.g. <initials>-<descriptive name>)")
    parser.add_option(
        "-t", "--timeout", action="store", type=int, dest="timeout",
        default=1800,
        help="timeout per task in seconds (default is 1800)")
    parser.add_option(
        "-m", "--memory", action="store", type=int, dest="memory",
        default=2048,
        help="memory limit per task in MB (default is 2048)")
    parser.add_option(
        "--shard-size", action="store", type=int, dest="shard_size",
        default=100,
        help="how many tasks to group into one top-level directory (default is 100)")
    parser.add_option(
        "--runs-per-task", action="store", type=int, dest="runs_per_task",
        default=1,
        help="how many runs to put into one task (default is 1)")
    parser.add_option(
        "--exp-root-dir", action="store", dest="exp_root_dir",
        default='../results',
        help="directory where all experiments are located (default is '../results'). " \
                "The new experiment will reside in <exp-root-dir>/<exp-name>")
    parser.add_option(
        "-d", "--debug", action="store_true", dest="debug",
        help="quick test mode: run search executable compiled with debug information, " + \
        "translate and preprocess if necessary, always conduct fresh search, " + \
        "print output to screen")
        
    options, args = parser.parse_args()
    
    if not options.exp_name:
        raise parser.error("You need to specify an experiment name")
        
    options.exp_type = options.exp_type.lower()
    if options.exp_type not in exp_types:
        parser.error('You need to specify one of %s as the experiment type' % exp_types)
    
    assert len(args) == 0
    return options
    
    
## Factory for experiments.
##
## Parses cmd-line options to decide whether this is a gkigrid
## experiment, a local experiment or whatever, and what the name
## of the experiment (the *.q file etc.) should be.
##
## Also parses options to override the default values for sharding
## (how many tasks to group into one top-level directory) and
## grouping (how many runs to put into one task).
##
## Maybe also parses some generic options that make sense for all
## kinds of experiments, e.g. timeout and memory limit.
def build_experiment():
    options = parse_options()
    exp = Experiment(options)
    return exp


if __name__ == "__main__":
    exp = build_experiment()
    exp.build()
