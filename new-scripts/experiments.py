#! /usr/bin/env python
"""
Main module for experiment creation
"""

from __future__ import with_statement

import os
import sys
import logging
import math

import tools
from external.ordereddict import OrderedDict

SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '../'))
DATA_DIR = os.path.join(SCRIPTS_DIR, 'data')

HELP = """\
Base module for creating fast downward experiments.
PLEASE NOTE: The available options depend on the selected experiment type.
You can set the experiment type with the "--exp-type" option.
"""

# Create a parser only for parsing the experiment type
exp_type_parser = tools.ArgParser(add_help=False, add_log_option=True)
exp_type_parser.add_argument('-e', '--exp-type', default='local',
                             choices=['local', 'gkigrid', 'argo'],
                             help='Select an experiment type')


class ExpArgParser(tools.ArgParser):
    def __init__(self, *args, **kwargs):
        parents = kwargs.pop('parents', []) + [exp_type_parser]
        tools.ArgParser.__init__(self, *args, parents=parents, **kwargs)

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
            help='directory where this experiment should be located '
                 '(default is this folder). '
                 'The new experiment will reside in <root-dir>/<name>')


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
            self.base_dir = self.name
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

    def add_resource(self, resource_name, source, dest, required=True):
        """
        Example:
        >>> experiment.add_resource('PLANNER', '../downward/search/downward',
                                    'downward')

        Includes a "global" file, i.e., one needed for all runs, into the
        experiment archive. In case of GkiGridExperiment, copies it to the
        main directory of the experiment. The name "PLANNER" is an ID for
        this resource that can also be used to refer to it in shell scripts.
        """
        dest = self._get_abs_path(dest)
        if not (source, dest) in self.resources:
            self.resources.append((source, dest, required))
        self.env_vars[resource_name] = dest

    def add_run(self, run=None):
        """
        Factory for Runs
        Schedule this run to be part of the experiment.
        """
        run = run or Run(self)
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
        def run_number(number):
            return str(number).zfill(5)

        def get_shard_dir(shard_number):
            first_run = self.shard_size * (shard_number - 1) + 1
            last_run = self.shard_size * (shard_number)
            return 'runs-%s-%s' % (run_number(first_run), run_number(last_run))

        current_run = 0

        shards = tools.divide_list(self.runs, self.shard_size)

        for shard_number, shard in enumerate(shards, start=1):
            shard_dir = os.path.join(self.base_dir,
                                     get_shard_dir(shard_number))
            tools.overwrite_dir(shard_dir)

            for run in shard:
                current_run += 1
                rel_dir = os.path.join(get_shard_dir(shard_number),
                                       run_number(current_run))
                abs_dir = os.path.join(self.base_dir, rel_dir)
                run.dir = abs_dir

    def _build_main_script(self):
        """
        Generates the main script
        """
        raise Exception('Not Implemented')

    def _build_resources(self):
        for source, dest, required in self.resources:
            logging.debug('Copying %s to %s' % (source, dest))
            try:
                tools.copy(source, dest, required)
            except IOError, err:
                msg = 'Error: The file "%s" could not be copied to "%s": %s'
                raise SystemExit(msg % (source, dest, err))

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
            '-j', '--processes', type=int, default=1,
            choices=xrange(1, cores + 1),
            help='number of parallel processes to use (default: 1)')
        Experiment.__init__(self, parser=parser)

        self.end_instructions = ('You can run the experiment now by calling '
            '"./%(name)s/run"' % {'name': self.name})

    def _build_main_script(self):
        """
        Generates the main script
        """
        dirs = [os.path.relpath(run.dir, self.base_dir) for run in self.runs]
        commands = ['"cd %s; ./run"' % dir for dir in dirs]
        replacements = {'COMMANDS': ',\n'.join(commands),
                        'PROCESSES': str(self.processes),
                        }

        script = open(os.path.join(DATA_DIR, 'local-job-template.py')).read()
        for orig, new in replacements.items():
            script = script.replace('***' + orig + '***', new)

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
            '--priority', type=int, default=0, choices=xrange(-1023, 1024 + 1),
            metavar='NUM', help='priority of the job [-1023, 1024]')

        Experiment.__init__(self, parser=parser)

        self.filename = self.name
        if not self.filename.endswith('.q'):
            self.filename += '.q'
        self.end_instructions = ('You can submit the experiment to the '
                        'queue now by calling "qsub ./%(name)s/%(filename)s"' %
                        self.__dict__)

    def _build_main_script(self):
        """
        Generates the main script
        """
        num_tasks = math.ceil(len(self.runs) / float(self.runs_per_task))
        job_params = {
            'logfile': self.name + '.log',
            'errfile': self.name + '.err',
            'driver_timeout': self.timeout * self.runs_per_task + 30,
            'num_tasks': num_tasks,
            'queue': self.queue,
            'priority': self.priority,
        }
        template_file = os.path.join(DATA_DIR, 'gkigrid-job-header-template')
        script_template = open(template_file).read()
        script = script_template % job_params

        script += '\n'

        run_groups = tools.divide_list(self.runs, self.runs_per_task)

        for task_id, run_group in enumerate(run_groups, start=1):
            script += 'if [[ $SGE_TASK_ID == %s ]]; then\n' % task_id
            for run in run_group:
                # Change into the run dir
                script += '  cd %s\n' % os.path.relpath(run.dir, self.base_dir)
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

        self.commands = OrderedDict()

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

    def add_resource(self, resource_name, source, dest, required=True):
        """
        Example:
        >>> run.add_resource('DOMAIN', '../benchmarks/gripper/domain.pddl',
                                'domain.pddl')

        Copy "../benchmarks/gripper/domain.pddl" into the run
        directory under name "domain.pddl" and make it available as
        resource "DOMAIN" (usable as environment variable $DOMAIN).
        """
        self.resources.append((source, dest, required))
        self.env_vars[resource_name] = dest

    def add_command(self, name, command, kwargs=None):
        """
        command has to be a list of strings
        kwargs is a dict that is passed to subprocess.Popen()
        """
        self.commands[name] = (command, kwargs or {})

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
        # Only this way we have all resources in self.resources
        # (linked ones too)
        self._build_linked_resources()
        self._build_run_script()
        self._build_resources()
        self._build_properties_file()

    def _build_run_script(self):
        if not self.commands:
            msg = 'Please add at least one command via run.add_command()'
            raise SystemExit(msg)

        run_script = open(os.path.join(DATA_DIR, 'run-template.py')).read()

        def make_call(name, cmd, kwargs):
            if not type(cmd) is list:
                logging.error('Commands have to be lists of strings. '
                              'The command <%s> is not a list.' % cmd)
                sys.exit(1)
            cmd_string = '[%s, %s]' % (cmd[0], ', '.join(repr(arg) for arg in cmd[1:]))
            kwargs_string = ', '.join('%s="%s"' % pair for pair in kwargs.items())
            parts = [cmd_string]
            if kwargs_string:
                parts.append(kwargs_string)
            call = 'retcode = Call(%s, **redirects).wait()\nsave_returncode("%s", retcode)\n'
            return call % (', '.join(parts), name)

        self.experiment.env_vars.update(self.env_vars)
        self.env_vars = self.experiment.env_vars.copy()

        if self.env_vars:
            env_vars_text = ''
            for var, filename in sorted(self.env_vars.items()):
                abs_filename = self._get_abs_path(filename)
                rel_filename = os.path.relpath(abs_filename, self.dir)
                env_vars_text += ('%s = "%s"\n' % (var, rel_filename))
        else:
            env_vars_text = ('"Here you would find the declaration of '
                             'environment variables"')
        run_script = run_script.replace('***ENVIRONMENT_VARIABLES***', env_vars_text)

        calls = [make_call(name, cmd, kwargs) for name, (cmd, kwargs) in self.commands.items()]
        run_script += '\n' + '\n'.join(calls)
        self.new_files.append(('run', run_script))
        return




        run_script = open(os.path.join(DATA_DIR, 'run-template.py')).read()
        resources = [filename for var, filename, req in self.resources]
        replacements = {'ENVIRONMENT_VARIABLES': env_vars_text,
                        'RUN_COMMAND': self.command,
                        'PREPROCESS_COMMAND': self.preprocess_command,
                        'POSTPROCESS_COMMAND': self.postprocess_command,
                        'TIMEOUT': str(self.experiment.timeout),
                        'MEMORY': str(self.experiment.memory),
                        'OPTIONAL_OUTPUT': str(self.optional_output),
                        'REQUIRED_OUTPUT': str(self.required_output),
                        'RESOURCES': str(resources)}
        for orig, new in replacements.items():
            run_script = run_script.replace('***' + orig + '***', new)

        self.new_files.append(('run', run_script))

    def _build_linked_resources(self):
        """
        If we are building an argo experiment, add all linked resources to
        the resources list
        """
        # Determine if we should link (gkigrid) or copy (argo)
        if type(self.experiment) == ArgoExperiment:
            # Copy into run dir by adding the linked resource to normal
            # resources list
            for resource_name in self.linked_resources:
                source = self.experiment.env_vars.get(resource_name, None)
                if not source:
                    logging.error('If you require a resource you have to add '
                                  'it to the experiment')
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

        for source, dest, required in self.resources:
            dest = self._get_abs_path(dest)
            logging.debug('Copying %s to %s' % (source, dest))
            try:
                tools.copy(source, dest, required)
            except IOError, err:
                msg = 'Error: The file "%s" could not be copied to "%s": %s'
                logging.error(msg % (source, dest, err))

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


def build_experiment(parser=ExpArgParser()):
    """
    Factory for experiments.

    Parses cmd-line options to decide whether this is a gkigrid
    experiment, a local experiment or whatever.
    """
    known_args, remaining_args = exp_type_parser.parse_known_args()

    type = known_args.exp_type
    logging.info('Experiment type: %s (Change with "--exp-type")' % type)

    parser.description = HELP

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
