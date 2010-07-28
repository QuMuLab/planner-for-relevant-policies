#! /usr/bin/env python
'''
Todo:
X OptionParser class
X optional/required outputs (warnings if more output)
X Inherit experiment classes from Experiment
X Put invoke code into run
X Write planner script
  X Suites
X LocalExperiment
X CL option for queue

X Try argparse in reports.py
O Convert code to use argparse
X Integrate txt2tags
X Use datasets
X Write AbsolutePlannerReport
X Write table to txt2tags function 
X Group by domain, problem, suite
X Comparative reports
X Relative reports
O Detailed reports

X Let user define wanted type for regexes
O Use double-quotes for multiline strings

O Vergleiche Ausgabe (v.a. expansions) des Translators, Prep., Search (Verwende athlon, opteron (mit core), schnell: amd, ausprobieren: xeon)
O lm-cut mit A* (ou), ob (LM blind), nicht nur STRIPS Domains, cea (yY), ff (fF), oa10000 (M&S)
  suites: ALL, lm-cut-domains
X #Operatoren, #Variablen, #Unterschiedliche Werte (Summe aller Werte) in properties file
X Anzahl Axiome in properties
X Anzahl Kanten im Causal Graph
X Schreibe queue in properties file
'''

from __future__ import with_statement

import os
import sys
import shutil
from optparse import OptionParser, OptionValueError, BadOptionError, Option
import logging
import math

logging.basicConfig(level=logging.INFO,
                    format='%(levelname)-8s %(message)s',)
                    
import tools
      
      

class ExpOptionParser(OptionParser):
    def __init__(self, *args, **kwargs):
        OptionParser.__init__(self, option_class=tools.ExtOption, *args, **kwargs)
      
        exp_types = ['local', 'gkigrid', 'argo']
        exp_types_string = ', '.join(['--'+type for type in exp_types])
        types_help = '(default: --local, use one of [%s])' % exp_types_string
        
        for type in exp_types:
            self.add_option(
                "--"+type, action="store_true", dest=type,
                help="create %s experiment %s" % (type, types_help))
        self.add_option(
            "-n", "--name", action="store", dest="exp_name", default="",
            help="name of the experiment (e.g. <initials>-<descriptive name>)")
        self.add_option(
            "-t", "--timeout", action="store", type=int, dest="timeout",
            default=1800,
            help="timeout per task in seconds (default is 1800)")
        self.add_option(
            "-m", "--memory", action="store", type=int, dest="memory",
            default=2048,
            help="memory limit per task in MB (default is 2048)")
        self.add_option(
            "--shard-size", action="store", type=int, dest="shard_size",
            default=100,
            help="how many tasks to group into one top-level directory (default is 100)")
        self.add_option(
            "--runs-per-task", action="store", type=int, dest="runs_per_task",
            default=1,
            help="how many runs to put into one task (default is 1)")
        self.add_option(
            "--exp-root-dir", action="store", dest="exp_root_dir",
            default='',
            help="directory where this experiment should be located (default is this folder). " \
                    "The new experiment will reside in <exp-root-dir>/<exp-name>")
        
    def error(self, msg):
        '''Show the complete help AND the error message'''
        self.print_help()
        OptionParser.error(self, msg)
        
    def parse_options(self):
        options, args = self.parse_args()
        
        if not options.exp_name:
            raise self.error("You need to specify an experiment name")
        
        return options
        


    

class Experiment(object):
    
    def __init__(self, parser=ExpOptionParser()):
        self.parser = parser
        options = self.parser.parse_options()
        # Give all the options to the experiment instance
        self.__dict__.update(options.__dict__)
        
        self.runs = []
        self.resources = []
        self.env_vars = {}
        
        if self.exp_root_dir:
            self.base_dir = os.path.join(self.exp_root_dir, self.exp_name)
        else:
            module_dir = os.path.dirname(__file__)
            self.base_dir = os.path.join(module_dir, self.exp_name)
        self.base_dir = os.path.abspath(self.base_dir)
        logging.info('Base Dir: "%s"' % self.base_dir)
        
        
        
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
        dest = self._get_abs_path(dest)
        self.resources.append((source, dest))
        if resource_name:
            self.env_vars[resource_name] = dest
        
    def add_run(self):
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
        tools.overwrite_dir(self.base_dir)
        
        self._set_run_dirs()
        self._build_main_script()
        self._build_resources()
        self._build_runs()
        
        
    def _get_abs_path(self, rel_path):
        '''
        Return absolute dir by applying rel_path to the experiment's base dir
        
        Example:
        >>> _get_abs_path('mytest.q')
        /home/user/mytestjob/mytest.q
        '''
        return os.path.join(self.base_dir, rel_path)
        

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
        
        shards = tools.divide_list(self.runs, self.shard_size)
        
        for shard_number, shard in enumerate(shards, start=1):
            shard_dir = os.path.join(self.base_dir, get_shard_dir(shard_number))
            tools.overwrite_dir(shard_dir)
            
            for run in shard:
                current_run += 1
                rel_dir = os.path.join(get_shard_dir(shard_number), get_run_number(current_run))
                abs_dir = os.path.join(self.base_dir, rel_dir)
                run.dir = abs_dir
        
        
    def _build_main_script(self):
        '''
        Generates the main script
        '''
        raise Exception('Not Implemented')
        
                
    def _build_resources(self):
        for source, dest in self.resources:
            logging.debug('Copying %s to %s' % (source, dest))
            try:
                shutil.copy2(source, dest)
            except IOError, err:
                raise SystemExit('Error: The file "%s" could not be copied to "%s": %s' % \
                                (source, dest, err))
                
                
    def _build_runs(self):
        '''
        Uses the relative directory information and writes all runs to disc
        '''
        for run in self.runs:
            run.build()
            
        
        
class LocalExperiment(Experiment):
    def __init__(self, parser=ExpOptionParser()):
        def check_and_store(dummy1, dummy2, value, parser):
            if value < 1:
                raise OptionValueError("number of processes must be at least 1")
            parser.values.processes = value
        parser.add_option(
            "-p", "--processes", type="int", dest="processes", default=1,
            action="callback", callback=check_and_store,
            help="number of parallel processes to use (default: 1)")
        Experiment.__init__(self, parser=parser)
        
        
    def _build_main_script(self):
        '''
        Generates the main script
        '''
        commands = ['"cd %s; ./run"' % run.dir for run in self.runs]
        replacements = {'COMMANDS': ',\n'.join(commands),
                        'PROCESSES': str(self.processes),
                        }
        
        script = open('data/local-job-template.py').read()
        for orig, new in replacements.items():
            script = script.replace('***'+orig+'***', new)
        
        filename = self._get_abs_path('run')
        
        with open(filename, 'w') as file:
            file.write(script)
            # Make run script executable
            os.chmod(filename, 0755)
        
        
        
class ArgoExperiment(Experiment):
    def __init__(self, parser=ExpOptionParser()):
        Experiment.__init__(self, parser=parser)
        


class GkiGridExperiment(Experiment):
    def __init__(self, parser=ExpOptionParser()):
        parser.add_option(
            "-q", "--queue", type="string", dest="queue", default='athlon_core.q',
            help="name of the queue to use for the experiment (default: athlon_core.q)")
        Experiment.__init__(self, parser=parser)
        
    def _build_main_script(self):
        '''
        Generates the main script
        '''
        num_tasks = math.ceil(len(self.runs) / float(self.runs_per_task))
        job_params = {
            "logfile": self.exp_name + ".log",
            "errfile": self.exp_name + ".err",
            "driver_timeout": self.timeout + 30,
            "num_tasks": num_tasks,
            "queue": self.queue,
        }
        script_template = open('data/gkigrid-job-header-template').read()
        script = script_template % job_params
        
        script += '\n'
        
        run_groups = tools.divide_list(self.runs, self.runs_per_task)
        
        for task_id, run_group in enumerate(run_groups, start=1):
            script += 'if [[ $SGE_TASK_ID == %s ]]; then\n' % task_id
            for run in run_group:
                # Change into the run dir
                script += '  cd %s\n' % run.dir
                script += '  ./run\n'
            script += 'fi\n'
                        
        
        name = self.exp_name
        filename = name if name.endswith('.q') else name + '.q'
        filename = self._get_abs_path(filename)
        
        with open(filename, 'w') as file:
            file.write(script)
    


class Run(object):
    '''
    A Task can consist of one or multiple Runs
    '''
    
    def __init__(self, experiment):
        self.experiment = experiment
        
        self.dir = ''
        
        self.resources = []
        self.linked_resources = []
        self.env_vars = {}
        self.new_files = []
        
        self.command = ''
        self.preprocess_command = ''
        self.postprocess_command = ''
        
        self.optional_output = []
        self.required_output = []
        
        self.properties = tools.Properties()
        
        if hasattr(experiment, 'queue'):
            self.set_property('queue', experiment.queue)
        
        
    def set_property(self, name, value):
        # id parts can only be strings
        if name == 'id':
            assert type(value) == list
            value = map(str, value)
        self.properties[name] = value
        
        
    def require_resource(self, resource_name):
        '''
        Some resources can be used by linking to the resource in the 
        experiment directory without copying it into each run
        
        In the argo cluster however, requiring a resource implies copying it
        into the task directory.
        
        Example:
        >>> run.require_resource("PLANNER")
        
        Make the planner resource available for this run
        In environments like the argo cluster, this implies
        copying the planner into each task. For the gkigrid, we merely
        need to set up the PLANNER environment variable.
        '''
        self.linked_resources.append(resource_name)
        
        
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
            self.env_vars[resource_name] = dest
            
                    
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
        self.optional_output.append(file_glob)
        
        
    def declare_required_output(self, filename):
        '''
        There's a corresponding declare_required_output for output
        files that must be present at the end or we have an error. A
        specification like this is e.g. necessary for the Argo
        cluster. On the gkigrid, this wouldn't do anything, although
        the declared outputs should be stored somewhere so that we
        can later verify that all went according to plan.
        '''
        self.required_output.append(filename)
        
        
    def build(self):
        '''
        After having made all the necessary adjustments with the methods above,
        this method can be used to write everything to the disk. 
        '''
        assert self.dir
        
        tools.overwrite_dir(self.dir)
        # We need to build the linked resources before the run script.
        # Only this way we have all resources in self.resources (linked ones too)
        self._build_linked_resources()
        self._build_run_script()
        self._build_resources()
        self._build_properties_file()
        
        
             
            
    def _build_run_script(self):
        if not self.command:
            raise SystemExit('You have to specify a command via run.set_command()')
            
        self.experiment.env_vars.update(self.env_vars)
        self.env_vars = self.experiment.env_vars.copy()
            
        if self.env_vars:
            env_vars_text = ''
            for var, filename in sorted(self.env_vars.items()):
                filename = self._get_abs_path(filename)
                env_vars_text += 'os.environ["%s"] = "%s"\n' % (var, filename)
        else:
            env_vars_text = '"Here you would find the declaration of environment variables"'
            
        run_script = open('data/gkigrid-run-template.py').read()
        replacements = {'ENVIRONMENT_VARIABLES': env_vars_text,
                        'RUN_COMMAND' :self.command,
                        'PREPROCESS_COMMAND': self.preprocess_command,
                        'POSTPROCESS_COMMAND': self.postprocess_command,
                        'TIMEOUT': str(self.experiment.timeout),
                        'MEMORY': str(self.experiment.memory),
                        'OPTIONAL_OUTPUT': str(self.optional_output),
                        'REQUIRED_OUTPUT': str(self.required_output),
                        'RESOURCES': str([filename for var, filename in self.resources])
                        }
        for orig, new in replacements.items():
            run_script = run_script.replace('***'+orig+'***', new)
        
        self.new_files.append(('run', run_script))
        
    
    def _build_linked_resources(self):
        '''
        If we are building an argo experiment, add all linked resources to
        the resources list
        '''
        # Determine if we should link (gkigrid) or copy (argo)
        copy = type(self.experiment) == ArgoExperiment
        if copy:
            # Copy into run dir by adding the linked resource to normal 
            # resources list
            for resource_name in self.linked_resources:
                source = self.experiment.env_vars.get(resource_name, None)
                if not source:
                    logging.error('If you require a resource you have to add it '
                                    'to the experiment')
                    sys.exit(1)
                basename = os.path.basename(source)
                dest = self._get_abs_path(basename)
                self.resources.append((source, dest))
        
        
    def _build_resources(self):
        for name, content in self.new_files:
            filename = self._get_abs_path(name)
            with open(filename, 'w') as file:
                logging.debug('Writing file "%s"' % filename)
                file.write(content)
                if name == 'run':
                    # Make run script executable
                    os.chmod(filename, 0755)
                    
        
                
        for source, dest in self.resources:
            dest = self._get_abs_path(dest)
            logging.debug('Copying %s to %s' % (source, dest))
            try:
                shutil.copy2(source, dest)
            except IOError, err:
                raise SystemExit('Error: The file "%s" could not be copied to "%s": %s' % \
                                (source, dest, err))
                                
    def _build_properties_file(self):
        self.properties.filename = self._get_abs_path('properties')
        self.properties.write()
                                
        
    def _get_abs_path(self, rel_path):
        '''
        Example:
        >>> _get_abs_path('run')
        /home/user/mytestjob/runs-00001-00100/run
        '''
        return os.path.join(self.dir, rel_path)
        
        
        
#EXPERIMENT_TYPES = {'local': LocalExperiment,
#                    'gkigrid': GkiGridExperiment,
#                    'argo': ArgoExperiment,
#                    }
    
    
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
def build_experiment(parser=None):
    exp = None
    args = map(str.lower, sys.argv)
    args = map(lambda arg: arg.strip('-'), args)
    
    exp_types = [(name.lower(), cls) for name, cls in globals().items() if 'Experiment' in name]
    
    
    for name, cls in exp_types:
        for arg in args:
            if name.startswith(arg):
                exp = cls(parser)
    if not exp:
        #Default or if '--local' in args:
        exp = LocalExperiment(parser)
    print exp
        
    assert exp
    return exp


if __name__ == "__main__":
    exp = build_experiment(ExpOptionParser())
    exp.build()
