#! /usr/bin/env python
"""
A module that has methods for checking out different revisions of the three
components of fast-downward (translate, preprocess, search) and performing
experiments with them.
"""
import os
import sys
import logging
import shlex

import experiments
import environments
import checkouts
import downward_suites
import downward_configs
import tools


PREPROCESSED_TASKS_DIR = os.path.join(tools.SCRIPTS_DIR, 'preprocessed-tasks')
tools.makedirs(PREPROCESSED_TASKS_DIR)


def _get_configs(planner_rev, config_list):
    """
    Turn the list of config names from the command line into a list of
    (config_nick, config_string) pairs
    """
    # New syntax <=> we use mercurial (hex, not numbers) or rev >= 4425
    try:
        rev_number = int(planner_rev)
    except ValueError:
        rev_number = None
    new_syntax = rev_number is None or rev_number >= 4425

    if new_syntax:
        # configs is a list of (nickname,config) pairs
        configs = downward_configs.get_configs(config_list)
    else:
        # Use the old config names
        # We use the config names also as nicknames
        configs = zip(config_list, config_list)
    return configs


def require_src_dirs(exp, combinations):
    import itertools
    checkouts = set(itertools.chain(*combinations))
    for checkout in checkouts:
        exp.add_resource('SRC_%s' % checkout.rev, checkout.src_dir,
                         'CODE-%s' % checkout.rev)


class DownwardRun(experiments.Run):
    def __init__(self, exp, translator, preprocessor, planner, problem):
        experiments.Run.__init__(self, exp)

        self.translator = translator
        self.preprocessor = preprocessor
        self.planner = planner

        self.problem = problem

        self.set_properties()

    def set_properties(self):
        self.domain_name = self.problem.domain
        self.problem_name = self.problem.problem

        self.set_property('translator', self.translator.rev)
        self.set_property('preprocessor', self.preprocessor.rev)
        self.set_property('planner', self.planner.rev)

        self.set_property('translator_parent', self.translator.parent_rev)
        self.set_property('preprocessor_parent', self.preprocessor.parent_rev)
        self.set_property('planner_parent', self.planner.parent_rev)

        self.set_property('domain', self.domain_name)
        self.set_property('problem', self.problem_name)

        # Add memory limit information in KB
        self.set_property('memory_limit', self.experiment.memory * 1024)


def _prepare_preprocess_run(exp, run):
    output_files = ["*.groups", "output.sas", "output"]

    run.require_resource(run.preprocessor.shell_name)

    run.add_resource("DOMAIN", run.problem.domain_file(), "domain.pddl")
    run.add_resource("PROBLEM", run.problem.problem_file(), "problem.pddl")

    run.add_command('translate', [run.translator.shell_name, 'domain.pddl',
                                   'problem.pddl'])
    run.add_command('preprocess', [run.preprocessor.shell_name],
                     {'stdin': 'output.sas'})

    ext_config = '-'.join([run.translator.rev, run.preprocessor.rev])
    run.set_property('config', ext_config)
    run.set_property('id', [ext_config, run.domain_name, run.problem_name])

    for output_file in output_files:
        run.declare_optional_output(output_file)


def _prepare_search_run(exp, run, config_nick, config):
    run.config_nick = config_nick
    run.planner_config = config

    run.require_resource(run.planner.shell_name)
    run.add_command('search', [run.planner.shell_name] +
                     shlex.split(run.planner_config), {'stdin': 'output'})
    run.declare_optional_output("sas_plan")

    # Validation
    run.require_resource('VALIDATE')
    run.add_command('validate', ['VALIDATE', 'DOMAIN', 'PROBLEM', 'sas_plan'])

    run.set_property('commandline_config', run.planner_config)

    # If all three parts have the same revision don't clutter the reports
    revs = [run.translator.rev, run.preprocessor.rev, run.planner.rev]
    if len(revs) == len(set(revs)):
        revs = [run.translator.rev]
    ext_config = '-'.join(revs + [config_nick])

    run.set_property('config', ext_config)
    run.set_property('id', [ext_config, run.domain_name, run.problem_name])


class DownwardExperiment(experiments.Experiment):
    def __init__(self, combinations, parser=None):
        self.combinations = combinations
        parser = parser or experiments.ExpArgParser()
        parser.add_argument('-p', '--preprocess', action='store_true',
                            help='build preprocessing experiment')
        parser.add_argument('--complete', action='store_true',
                            help='build complete experiment (overrides -p)')
        parser.add_argument('-s', '--suite', default=[], type=tools.csv,
                            required=True, help=downward_suites.HELP)
        parser.add_argument('-c', '--configs', default=[], type=tools.csv,
                            required=False, help=downward_configs.HELP)

        experiments.Experiment.__init__(self, parser)

        config_needed = self.complete or not self.preprocess
        if config_needed and not self.configs:
            logging.error('Please specify at least one planner configuration')
            sys.exit(2)

        checkouts.make_checkouts(combinations)
        #require_src_dirs(self, combinations)
        self.problems = downward_suites.build_suite(self.suite)

        self.prepare()
        self.make_runs()

    def _require_checkout(self, part):
        self.add_resource(part.shell_name, part.binary, part.rel_dest)

    def prepare(self):
        if self.preprocess:
            self._prepare_preprocess()

    def _prepare_preprocess(self):
        """
        When the option --preprocess is passed on the commandline this method
        is invoked and it creates a preprocessing experiment.

        When the resultfetcher is run the following directory structure is created:

        SCRIPTS_DIR
            - preprocessed-tasks
                - TRANSLATOR_REV-PREPROCESSOR_REV
                    - DOMAIN
                        - PROBLEM
                            - output
        """
        # Use unique name for the preprocess experiment
        if not self.name.endswith('-p'):
            self.name += '-p'
            logging.info('Experiment name set to %s' % self.name)

        # Use unique dir for the preprocess experiment
        if not self.base_dir.endswith('-p'):
            self.base_dir += '-p'
            logging.info('Experiment directory set to %s' % self.base_dir)

        # Add some instructions
        if self.environment == environments.LocalEnvironment:
            self.end_instructions = ('Preprocess experiment has been created. '
                'Before you can create the search experiment you have to run\n'
                './%(exp_name)s/run\n'
                './resultfetcher.py %(exp_name)s' % {'exp_name': self.name})
        elif self.environment == environments.GkiGridEnvironment:
            exp.end_instructions = ('You can submit the preprocessing '
                'experiment to the queue now by calling '
                '"qsub ./%(name)s/%(filename)s"' % self.__dict__)

        # Set the eval directory already here, we don't want the results to land
        # in the default testname-eval
        self.set_property('eval_dir', os.path.relpath(PREPROCESSED_TASKS_DIR))

        # We need the "output" file, not only the properties file
        self.set_property('copy_all', True)

    def _prepare_translator_and_preprocessor(self, translator, preprocessor):
        # Copy the whole translate directory
        self.add_resource(translator.shell_name + '_DIR', translator.exe_dir,
                         translator.rel_dest)
        # In order to set an environment variable, overwrite the executable
        self.add_resource(translator.shell_name,
                         os.path.join(translator.exe_dir, 'translate.py'),
                         os.path.join(translator.rel_dest, 'translate.py'))
        self._require_checkout(preprocessor)

    def _prepare_planner(self, planner):
        self._require_checkout(planner)
        for bin in ['downward-1', 'downward-2', 'downward-4', 'dispatch',
                    'downward-seq-opt-fdss-1.py', 'unitcost']:
            src_path = os.path.join(planner.exe_dir, bin)
            if not os.path.isfile(src_path):
                continue
            code_subdir = os.path.dirname(planner.rel_dest)
            self.add_resource('UNUSEDNAME', src_path,
                            os.path.join(code_subdir, bin))
        validate = os.path.join(planner.exe_dir, '..', 'validate')
        if os.path.exists(validate):
            self.add_resource('VALIDATE', validate, 'validate')

    def _get_configs(self, rev):
        return _get_configs(rev, self.configs)

    def make_runs(self):
        if self.complete:
            self._make_complete_runs()
        elif self.preprocess:
            self._make_preprocess_runs()
        else:
            self._make_search_runs()

    def _make_preprocess_runs(self):
        for translator, preprocessor, planner in self.combinations:
            self._prepare_translator_and_preprocessor(translator, preprocessor)

            for prob in self.problems:
                run = DownwardRun(self, translator, preprocessor, planner, prob)
                _prepare_preprocess_run(self, run)
                self.add_run(run)

    def _make_search_runs(self):
        for translator, preprocessor, planner in self.combinations:
            self._prepare_planner(planner)

            for config_nick, config in self._get_configs(planner.rev):
                for prob in self.problems:
                    run = DownwardRun(self, translator, preprocessor, planner, prob)
                    _prepare_search_run(self, run, config_nick, config)
                    self.add_run(run)

                    preprocess_dir = os.path.join(PREPROCESSED_TASKS_DIR,
                                    translator.rev + '-' + preprocessor.rev,
                                    prob.domain, prob.problem)

                    def path(filename):
                        return os.path.join(preprocess_dir, filename)

                    # Add the preprocess files for later parsing
                    run.add_resource('OUTPUT', path('output'), 'output',
                                     required=False)
                    run.add_resource('TEST_GROUPS', path('test.groups'),
                                     'test.groups', required=False)
                    run.add_resource('ALL_GROUPS', path('all.groups'),
                                     'all.groups', required=False)
                    run.add_resource('OUTPUT_SAS', path('output.sas'),
                                     'output.sas', required=False)
                    run.add_resource('RUN_LOG', path('run.log'), 'run.log')
                    run.add_resource('RUN_ERR', path('run.err'), 'run.err')
                    run.add_resource('DOMAIN', path('domain.pddl'),
                                     'domain.pddl')
                    run.add_resource('PROBLEM', path('problem.pddl'),
                                     'problem.pddl')

    def _make_complete_runs(self):
        for translator, preprocessor, planner in self.combinations:
            self._prepare_translator_and_preprocessor(translator, preprocessor)
            self._prepare_planner(planner)

            for config_nick, config in self._get_configs(planner.rev):
                for prob in self.problems:
                    run = DownwardRun(self, translator, preprocessor, planner, prob)
                    _prepare_preprocess_run(self, run)
                    _prepare_search_run(self, run, config_nick, config)
                    self.add_run(run)


def build_experiment(combinations):
    for translator, preprocessor, planner in combinations:
        assert translator.part == 'translate'
        assert preprocessor.part == 'preprocess'
        assert planner.part == 'search'

    exp = DownwardExperiment(combinations)
    exp.build()


if __name__ == '__main__':
    combinations = [(checkouts.TranslatorHgCheckout(rev='WORK'),
                     checkouts.PreprocessorHgCheckout(rev='WORK'),
                     checkouts.PlannerHgCheckout(rev='WORK'))]

    build_experiment(combinations)
