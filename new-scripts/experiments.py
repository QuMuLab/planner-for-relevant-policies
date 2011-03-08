#! /usr/bin/env python
"""
Main module for experiment creation
"""

from __future__ import with_statement

import os
import sys
import logging

import environments
import tools
from external.ordereddict import OrderedDict


HELP = """\
Base module for creating fast downward experiments.
PLEASE NOTE: The available options depend on the selected experiment type.
You can set the experiment type with the "--exp-type" option.
"""

ENVIRONMENTS = {'local': environments.LocalEnvironment,
                'gkigrid': environments.GkiGridEnvironment,
                'argo': environments.ArgoEnvironment}

DEFAULT_ABORT_ON_FAILURE = True


class ExpArgParser(tools.ArgParser):
    def __init__(self, *args, **kwargs):
        tools.ArgParser.__init__(self, *args, **kwargs)

        self.add_argument('-p', '--path',
            help='path of the experiment (e.g. <initials>-<descriptive name>)')
        self.add_argument(
            '-t', '--timeout', type=int, default=1800,
            help='timeout per task in seconds')
        self.add_argument(
            '-m', '--memory', type=int, default=2048,
            help='memory limit per task in MB')
        self.add_argument(
            '--shard-size', type=int, default=100,
            help='how many tasks to group into one top-level directory')


class Experiment(object):
    def __init__(self, parser=None):
        self.environment = None
        self.end_instructions = ''

        self.runs = []
        self.resources = []
        self.env_vars = {}

        self.properties = tools.Properties()

        self.set_property('commandline_string', ' '.join(sys.argv))

        # Give all the options to the experiment instance
        self.parser = parser or ExpArgParser()
        self.parse_args()
        assert self.environment
        self.path = os.path.abspath(self.path)

        # Derive the experiment name from the path
        self.name = os.path.basename(self.path)

        logging.info('Exp Dir: "%s"' % self.path)

        # Include the experiment code
        self.add_resource('CALLS', tools.CALLS_DIR, 'calls')

    def parse_args(self):
        subparsers = self.parser.add_subparsers(dest='environment_type')
        for cls in ENVIRONMENTS.values():
            cls.add_subparser(subparsers)
        self.parser.parse_args(namespace=self)
        logging.info('Environment: %s' % self.environment_type)
        self.environment = ENVIRONMENTS.get(self.environment_type)
        if not self.environment:
            logging.error('Unknown environment "%s"' % self.environment_type)
            sys.exit(1)
        while not self.path:
            self.path = raw_input('Please enter an experiment path: ').strip()

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
        tools.overwrite_dir(self.path)

        # Make the variables absolute
        self.env_vars = dict([(var, self._get_abs_path(path))
                              for (var, path) in self.env_vars.items()])

        self._set_run_dirs()
        self._build_main_script()
        self._build_resources()
        self._build_runs()
        self._build_properties_file()

        # Print some instructions for further processing at the end
        self.end_instructions = (self.end_instructions or
                                 self.environment.get_end_instructions(self))
        if self.end_instructions:
            logging.info(self.end_instructions)

    def _get_abs_path(self, rel_path):
        """
        Return absolute dir by applying rel_path to the experiment's base dir

        Example:
        >>> _get_abs_path('mytest.q')
        /home/user/mytestjob/mytest.q
        """
        return os.path.join(self.path, rel_path)

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
            shard_dir = os.path.join(self.path, get_shard_dir(shard_number))
            tools.overwrite_dir(shard_dir)

            for run in shard:
                current_run += 1
                rel_dir = os.path.join(get_shard_dir(shard_number),
                                       run_number(current_run))
                run.dir = self._get_abs_path(rel_dir)

    def _build_main_script(self):
        """
        Generates the main script
        """
        self.environment.write_main_script(self)

    def _build_resources(self):
        for source, dest, required in self.resources:
            dest = self._get_abs_path(dest)
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
        num_runs = len(self.runs)
        self.set_property('runs', num_runs)
        logging.info('Building %d runs' % num_runs)
        for index, run in enumerate(self.runs, 1):
            run.build()
            if index % 100 == 0:
                logging.info('Built run %6d/%d' % (index, num_runs))

    def _build_properties_file(self):
        self.properties.filename = self._get_abs_path('properties')
        self.properties.write()


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

    def add_command(self, name, command, **kwargs):
        """Adds a command to the run.

        "name" is the command's name.
        "command" has to be a list of strings.

        The items in kwargs are passed to the calls.call.Call() class. You can
        find the valid keys there.

        kwargs can also contain a value for "abort_on_failure" which makes the
        run abort if the command does not return 0.

        The remaining items in kwargs are passed to subprocess.Popen()
        The allowed parameters can be found at
        http://docs.python.org/library/subprocess.html

        Examples:
        >>> run.add_command('translate', [run.translator.shell_name,
                                          'domain.pddl', 'problem.pddl'])
        >>> run.add_command('preprocess', [run.preprocessor.shell_name],
                            {'stdin': 'output.sas'})
        >>> run.add_command('validate', ['VALIDATE', 'DOMAIN', 'PROBLEM',
                                         'sas_plan'])

        """
        assert type(name) is str, 'The command name must be a string'
        assert type(command) in (tuple, list), 'The command must be a list'
        name = name.replace(' ', '_')
        self.commands[name] = (command, kwargs)

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

        self.experiment.env_vars.update(self.env_vars)
        self.env_vars = self.experiment.env_vars.copy()

        run_script = open(os.path.join(tools.DATA_DIR, 'run-template.py')).read()

        def make_call(name, cmd, kwargs):
            abort_on_failure = kwargs.pop('abort_on_failure',
                                          DEFAULT_ABORT_ON_FAILURE)
            if not type(cmd) is list:
                logging.error('Commands have to be lists of strings. '
                              'The command <%s> is not a list.' % cmd)
                sys.exit(1)
            if not cmd:
                logging.error('Command "%s" cannot be empty' % name)
                sys.exit(1)

            # Support running globally installed binaries
            def format_arg(arg):
                if arg in self.env_vars:
                    return arg
                return '"%s"' % arg

            cmd_string = '[%s]' % ', '.join([format_arg(arg) for arg in cmd])
            kw_pairs = [(key, repr(value)) for
                        (key, value) in kwargs.items()]
            kwargs_string = ', '.join('%s=%s' % pair for pair in kw_pairs)
            parts = [cmd_string]
            if kwargs_string:
                parts.append(kwargs_string)
            call = ('retcode = Call(%s, **redirects).wait()\n'
                    'save_returncode("%s", retcode)\n') % (', '.join(parts), name)
            if abort_on_failure:
                call += ('if not retcode == 0:\n'
                         '    sys.exit("%s returned %%s" %% retcode)\n' % name)
            return call

        calls_text = '\n'.join(make_call(name, cmd, kwargs)
                               for name, (cmd, kwargs) in self.commands.items())

        if self.env_vars:
            env_vars_text = ''
            for var, filename in sorted(self.env_vars.items()):
                abs_filename = self._get_abs_path(filename)
                rel_filename = os.path.relpath(abs_filename, self.dir)
                env_vars_text += ('%s = "%s"\n' % (var, rel_filename))
        else:
            env_vars_text = '"Here you would find variable declarations"'

        for old, new in [('VARIABLES', env_vars_text), ('CALLS', calls_text)]:
            run_script = run_script.replace('"""%s"""' % old, new)

        self.new_files.append(('run', run_script))
        return

    def _build_linked_resources(self):
        """
        If we are building an argo experiment, add all linked resources to
        the resources list
        """
        # Determine if we should link (gkigrid) or copy (argo)
        if self.experiment.environment == environments.ArgoEnvironment:
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


if __name__ == '__main__':
    exp = Experiment()
    exp.build()
