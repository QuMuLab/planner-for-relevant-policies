#! /usr/bin/env python
"""
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
X Convert code to use argparse
X Integrate txt2tags
X Use datasets
X Write AbsolutePlannerReport
X Write table to txt2tags function 
X Group by domain, problem, suite
X Comparative reports
X Relative reports
O Detailed reports

X Let user define wanted type for regexes
X Use double-quotes for multiline strings

X Vergleiche Ausgabe (v.a. expansions) des Translators, Prep., Search (Verwende athlon, opteron (mit core), schnell: amd, ausprobieren: xeon)
X lm-cut mit A* (ou), ob (LM blind), nicht nur STRIPS Domains, cea (yY), ff (fF), oa10000 (M&S)
  suites: ALL, lm-cut-domains
  configs: 
    - ou, ob, oa10000 (LMCUT)
    - yY, fF (ALL)
X #Operatoren, #Variablen, #Unterschiedliche Werte (Summe aller Werte) in properties file
X Anzahl Axiome in properties
X Anzahl Kanten im Causal Graph
X Schreibe queue in properties file
X Derived Vars in properties
X Write high-level documentation

X Report multiple attributes at once
X Colors for txt2tags
X Grey out rows that have equal numbers

X Add priority option for gkigrid experiments

X Unify evaluations
X Add copy-all parameter
X Only compare those problems that have been solved by all configs
O Handle iterative planner results
X Ask about DataSet dict access method returning lists or values
X Global experiment properties file
"""

from __future__ import with_statement

import os
import sys
import shutil
import logging
import math

logging.basicConfig(level=logging.INFO, format='%(asctime)-s %(levelname)-8s %(message)s',)
                    
import tools
      
      
      
# Create a parser only for parsing the experiment type
exp_type_parser = tools.ArgParser(add_help=False)
exp_type_parser.add_argument('-e', '--exp_type', choices=['local', 'gkigrid', 'argo'],
                                default='local', help='Select an experiment type')
      

class ExpArgParser(tools.ArgParser):
    def __init__(self, *args, **kwargs):
        tools.ArgParser.__init__(self, *args, parents=[exp_type_parser], **kwargs)
      
        self.add_argument('name', 
                    help='name of the experiment (e.g. <initials>-<descriptive name>)')
        self.add_argument(
            '-t', '--timeout', type=int, default=1800,
            help='timeout per task in seconds')
        self.add_argument(
            '-m', '--memory', type=int, default=2048,
            help='memory limit per task in MB')
        self.add_argument(
            '--shard-size', type=int, default=100,
            help='how many tasks to group into one top-level directory')
        self.add_argument(
            '--root-dir', 
            help='directory where this experiment should be located (default is this folder). ' \
                    'The new experiment will reside in <root-dir>/<exp-name>')
        
    

class Experiment(object):
    def __init__(self, parser=ExpArgParser()):
        # Give all the options to the experiment instance
        parser.parse_args(namespace=self)
        
        self.runs = []
        self.resources = []
        self.env_vars = {}
        
        # Print some instructions for further processing at the end
        self.end_instructions = ''
        
        self.properties = tools.Properties()
        
        if self.root_dir:
            self.base_dir = os.path.join(self.root_dir, self.name)
        else:
            module_dir = os.path.dirname(__file__)
            self.base_dir = os.path.join(module_dir, self.name)
        self.base_dir = os.path.abspath(self.base_dir)
        logging.info('Base Dir: "%s"' % self.base_dir)
        
    def set_property(self, name, value):
        """
        Add a key-value property to the experiment. These can be used later for 
        evaluation
        
        Example:
        >>> exp.set_property('translator', '4321')
        """
        # id parts can only be strings
        if name == 'id':
            assert type(value) == list, value
            value = map(str, value)
        self.properties[name] = value
        
    def add_resource(self, resource_name, source, dest):
        """
        Example:
        >>> experiment.add_resource('PLANNER', '../downward/search/release-search',
                                    'release-search')
                                    
        Includes a "global" file, i.e., one needed for all runs, into the
        experiment archive. In case of GkiGridExperiment, copies it to the
        main directory of the experiment. The name "PLANNER" is an ID for
        this resource that can also be used to refer to it in shell scripts.
        """
        dest = self._get_abs_path(dest)
        if not (source, dest) in self.resources:
            self.resources.append((source, dest))
        self.env_vars[resource_name] = dest
        
    def add_run(self):
        """
        Factory for Runs
        Schedule this run to be part of the experiment.
        """
        run = Run(self)
        self.runs.append(run)
        return run
        
    def build(self):
        """
        Apply all the actions to the filesystem
        """
        tools.overwrite_dir(self.base_dir)
        
        self._set_run_dirs()
        self._build_main_script()
        self._build_resources()
        self._build_runs()
        self._build_properties_file()
        
        if self.end_instructions:
            logging.info(self.end_instructions)
        
        
    def _get_abs_path(self, rel_path):
        """
        Return absolute dir by applying rel_path to the experiment's base dir
        
        Example:
        >>> _get_abs_path('mytest.q')
        /home/user/mytestjob/mytest.q
        """
        return os.path.join(self.base_dir, rel_path)
        

    def _set_run_dirs(self):
        """
        Sets the relative run directories as instance 
        variables for all runs
        """
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
        """
        Generates the main script
        """
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
        """
        Uses the relative directory information and writes all runs to disc
        """
        for run in self.runs:
            run.build()
            
    
    def _build_properties_file(self):
        self.properties.filename = self._get_abs_path('properties')
        self.properties.write()
            
        
        
class LocalExperiment(Experiment):
    def __init__(self, parser=ExpArgParser()):
        import multiprocessing
        cores = multiprocessing.cpu_count()
        parser.add_argument(
            '-j', '--processes', type=int, default=1, choices=xrange(1, cores+1),
            help='number of parallel processes to use (default: 1)')
        Experiment.__init__(self, parser=parser)
        
        self.end_instructions = 'You can run the experiment now by calling ' \
            '"./%(name)s/run"' % {'name': self.name}
        
        
    def _build_main_script(self):
        """
        Generates the main script
        """
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
    def __init__(self, parser=ExpArgParser()):
        Experiment.__init__(self, parser=parser)
        


class GkiGridExperiment(Experiment):
    def __init__(self, parser=ExpArgParser()):        
        parser.add_argument(
            '-q', '--queue', default='athlon_core.q',
            help='name of the queue to use for the experiment')
        parser.add_argument(
            '--runs-per-task', type=int, default=1,
            help='how many runs to put into one task')
        parser.add_argument(
            '--priority', type=int, default=0, choices=xrange(-1023, 1024+1),
            metavar='NUM', help='priority of the job [-1023, 1024]')
            
        Experiment.__init__(self, parser=parser)
        
        self.filename = self.name if self.name.endswith('.q') else self.name + '.q'
        self.end_instructions = 'You can run submit the experiment to the ' \
            'queue now by calling "qsub ./%(name)s/%(filename)s"' % self.__dict__
        
        
    def _build_main_script(self):
        """
        Generates the main script
        """
        num_tasks = math.ceil(len(self.runs) / float(self.runs_per_task))
        current_dir = os.path.dirname(os.path.abspath(__file__))
        job_params = {
            'logfile': os.path.join(current_dir, self.name, self.name + '.log'),
            'errfile': os.path.join(current_dir, self.name, self.name + '.err'),
            'driver_timeout': self.timeout + 30,
            'num_tasks': num_tasks,
            'queue': self.queue,
            'priority': self.priority,
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
        
        self.filename = self._get_abs_path(self.filename)
        
        with open(self.filename, 'w') as file:
            file.write(script)
    


class Run(object):
    """
    A Task can consist of one or multiple Runs
    """
    
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
        """
        Add a key-value property to a run. These can be used later for 
        evaluation
        
        Example:
        >>> run.set_property('domain', 'gripper')
        """
        # id parts can only be strings
        if name == 'id':
            assert type(value) == list
            value = map(str, value)
        self.properties[name] = value
        
        
    def require_resource(self, resource_name):
        """
        Some resources can be used by linking to the resource in the 
        experiment directory without copying it into each run
        
        In the argo cluster however, requiring a resource implies copying it
        into the task directory.
        
        Example:
        >>> run.require_resource('PLANNER')
        
        Make the planner resource available for this run
        In environments like the argo cluster, this implies
        copying the planner into each task. For the gkigrid, we merely
        need to set up the PLANNER environment variable.
        """
        self.linked_resources.append(resource_name)
        
        
    def add_resource(self, resource_name, source, dest):
        """
        Example:
        >>> run.add_resource('DOMAIN', '../benchmarks/gripper/domain.pddl',
                                'domain.pddl')
                                
        Copy "../benchmarks/gripper/domain.pddl" into the run
        directory under name "domain.pddl" and make it available as
        resource "DOMAIN" (usable as environment variable $DOMAIN).
        """        
        self.resources.append((source, dest))
        self.env_vars[resource_name] = dest
            
                    
    def set_command(self, command):
        """
        Example:
        >>> run.set_command('$PLANNER %s <$INFILE' % options)
        
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
        """
        self.command = command
        
    def set_preprocess(self, command):
        """
        Execute a command prior tu running the main command
        
        Example:
        >>> run.set_preprocess('ls -la')
        """
        self.preprocess_command = command
        
    def set_postprocess(self, command):
        """
        Execute a command directly after the main command exited
        
        Example:
        >>> run.set_postprocess('echo Finished')
        """
        self.postprocess_command = command
        
        
    def declare_optional_output(self, file_glob):
        """
        Example:
        >>> run.declare_optional_output('plan.soln*')
        
        Specifies that all files names "plan.soln*" (using
        shell-style glob patterns) are part of the experiment output.
        """
        self.optional_output.append(file_glob)
        
        
    def declare_required_output(self, filename):
        """
        Declare output files that must be present at the end or we have an 
        error. A specification like this is e.g. necessary for the Argo
        cluster. On the gkigrid, this wouldn't do anything, although
        the declared outputs should be stored somewhere so that we
        can later verify that all went according to plan.
        """
        self.required_output.append(filename)
        
        
    def build(self):
        """
        After having made all the necessary adjustments with the methods above,
        this method can be used to write everything to the disk. 
        """
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
            
        run_script = open('data/run-template.py').read()
        replacements = {'ENVIRONMENT_VARIABLES': env_vars_text,
                        'RUN_COMMAND' : self.command,
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
        """
        If we are building an argo experiment, add all linked resources to
        the resources list
        """
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
        """
        Example:
        >>> _get_abs_path('run')
        /home/user/mytestjob/runs-00001-00100/run
        """
        return os.path.join(self.dir, rel_path)
        
    
    
## Factory for experiments.
##
## Parses cmd-line options to decide whether this is a gkigrid
## experiment, a local experiment or whatever.
def build_experiment(parser=ExpArgParser()):
    known_args, remaining_args = exp_type_parser.parse_known_args()
    
    type = known_args.exp_type
    logging.info('Experiment type: %s' % type)
    
    parser.epilog = 'Note: The help output depends on the selected experiment type'
    
    if type == 'local':
        exp = LocalExperiment(parser)
    elif type == 'gkigrid':
        exp = GkiGridExperiment(parser)
    elif type == 'argo':
        exp = ArgoExperiment(parser)
    return exp


if __name__ == '__main__':
    exp = build_experiment()
    exp.build()
