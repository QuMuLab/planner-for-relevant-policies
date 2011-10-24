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


LIMIT_TRANSLATE_TIME = 7200
LIMIT_TRANSLATE_MEMORY = 8192
LIMIT_PREPROCESS_TIME = 7200
LIMIT_PREPROCESS_MEMORY = 8192
LIMIT_SEARCH_TIME = 1800
LIMIT_SEARCH_MEMORY = 2048

# At least one of those must be found (First is taken if many are present)
PLANNER_BINARIES = ['downward', 'downward-debug', 'downward-profile',
                    'release-search', 'search']
# The following are added only if they are present
PLANNER_HELPERS = ['downward-1', 'downward-2', 'downward-4', 'dispatch',
                   'seq_opt_portfolio.py', 'seq_sat_portfolio.py', 'unitcost']


def shell_escape(s):
    return s.upper().replace('-', '_').replace(' ', '_').replace('.', '_')


def _get_configs(config_and_porfolio_list):
    """
    Turn the list of config names from the command line into a list of
    (config_nick, config_string) pairs
    """
    portfolios = []
    config_nicks = []
    for name in config_and_porfolio_list:
        if name.endswith('.py'):
            portfolios.append((name, ''))
        else:
            config_nicks.append(name)

    # configs is a list of (config_nick, config) pairs
    configs = downward_configs.get_configs(config_nicks)
    return configs + portfolios


def require_src_dirs(exp, combinations):
    import itertools
    checkouts = set(itertools.chain(*combinations))
    for checkout in checkouts:
        exp.add_resource('SRC_%s' % checkout.name, checkout.src_dir,
                         'code-%s' % checkout.name)


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

        self.set_property('limit_translate_time', LIMIT_TRANSLATE_TIME)
        self.set_property('limit_translate_memory', LIMIT_TRANSLATE_MEMORY)
        self.set_property('limit_preprocess_time', LIMIT_PREPROCESS_TIME)
        self.set_property('limit_preprocess_memory', LIMIT_PREPROCESS_MEMORY)
        self.set_property('limit_search_time', LIMIT_SEARCH_TIME)
        self.set_property('limit_search_memory', LIMIT_SEARCH_MEMORY)

        self.set_property('experiment_name', self.experiment.name)


def _prepare_preprocess_run(exp, run):
    output_files = ["*.groups", "output.sas", "output"]

    run.require_resource(run.preprocessor.shell_name)

    run.add_resource("DOMAIN", run.problem.domain_file(), "domain.pddl")
    run.add_resource("PROBLEM", run.problem.problem_file(), "problem.pddl")

    run.add_command('translate', [run.translator.shell_name, 'DOMAIN',
                                  'PROBLEM'],
                    time_limit=LIMIT_TRANSLATE_TIME,
                    mem_limit=LIMIT_TRANSLATE_MEMORY)
    run.add_command('preprocess', [run.preprocessor.shell_name],
                    stdin='output.sas',
                    time_limit=LIMIT_PREPROCESS_TIME,
                    mem_limit=LIMIT_PREPROCESS_MEMORY)

    ext_config = '-'.join([run.translator.name, run.preprocessor.name])
    run.set_property('config', ext_config)
    run.set_property('id', [ext_config, run.domain_name, run.problem_name])

    for output_file in output_files:
        run.declare_optional_output(output_file)


def _prepare_search_run(exp, run, config_nick, config):
    """
    If preprocess_dir is None we are assuming all relevant files are present
    in the dir (output, domain.pddl, problem.pddl).
    Else we use the absolute paths to the preprocess_dir to specify these
    files.
    """
    run.require_resource(run.planner.shell_name)
    if config:
        # We have a single planner configuration
        config = config.replace('\n', ' ').replace('\t', ' ')
        search_cmd = [run.planner.shell_name] + shlex.split(config)
    else:
        # We have a portfolio, config_nick is the path to the portfolio file
        config_nick = os.path.basename(config_nick)
        search_cmd = [run.planner.shell_name, '--portfolio', config_nick,
                      '--plan-file', 'sas_plan']
    run.add_command('search', search_cmd, stdin='output',
                    time_limit=LIMIT_SEARCH_TIME,
                    mem_limit=LIMIT_SEARCH_MEMORY,
                    abort_on_failure=False)
    run.declare_optional_output("sas_plan")

    # Validation
    run.require_resource('VALIDATE')
    run.require_resource('DOWNWARD_VALIDATE')
    run.add_command('validate', ['DOWNWARD_VALIDATE', 'VALIDATE', 'DOMAIN',
                                 'PROBLEM'])

    run.set_property('config_nick', config_nick)
    run.set_property('commandline_config', config)

    # If all three parts have the same revision don't clutter the reports
    names = [run.translator.name, run.preprocessor.name, run.planner.name]
    if len(set(names)) == 1:
        names = [run.translator.name]
    ext_config = '-'.join(names + [config_nick])

    run.set_property('config', ext_config)
    run.set_property('id', [ext_config, run.domain_name, run.problem_name])


class DownwardExperiment(experiments.Experiment):
    def __init__(self, combinations, parser=None):
        self.combinations = combinations
        parser = parser or experiments.ExpArgParser()
        parser.add_argument('--preprocess', action='store_true',
                            help='build preprocessing experiment')
        parser.add_argument('--complete', action='store_true',
                            help='build complete experiment (overrides -p)')
        compact_help = ('link to preprocessing files instead of copying them. '
                        'Only use this option if the preprocessed files will '
                        'NOT be changed during the experiment. This option '
                        'only has an effect if neither --preprocess nor '
                        '--complete are set.')
        parser.add_argument('--compact', action='store_true',
                            help=compact_help)
        parser.add_argument('-s', '--suite', default=[], type=tools.csv,
                            required=True, help=downward_suites.HELP)
        parser.add_argument('-c', '--configs', default=[], type=tools.csv,
                            required=False, dest='config_nicks',
                            help=downward_configs.HELP)

        experiments.Experiment.__init__(self, parser)

        config_needed = self.complete or not self.preprocess
        if config_needed and not self.config_nicks:
            logging.error('Please specify at least one planner configuration')
            sys.exit(2)

        # Save if this is a compact experiment i.e. preprocess files are copied
        compact = self.compact and not self.preprocess and not self.complete
        self.set_property('compact', compact)

        checkouts.checkout(combinations)
        checkouts.compile(combinations)
        #require_src_dirs(self, combinations)
        self.problems = downward_suites.build_suite(self.suite)
        self.configs = _get_configs(self.config_nicks)

        self.make_runs()

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
        if not self.path.endswith('-p'):
            self.path += '-p'
            logging.info('Experiment directory set to %s' % self.path)

        # Add some instructions
        if self.environment == environments.LocalEnvironment:
            self.end_instructions = ('Preprocess experiment has been created. '
                'Before you can create the search experiment you have to run\n'
                '%(run_script)s\n'
                './resultfetcher.py %(exp_path)s' %
                {'run_script': self.compact_main_script_path,
                 'exp_path': self.compact_exp_path})

        # Set the eval directory already here, we don't want the results to
        # land in the default testname-eval
        self.set_property('eval_dir', os.path.relpath(PREPROCESSED_TASKS_DIR))

        # We need the "output" file, not only the properties file
        self.set_property('copy_all', True)

        # Don't write the combined properties file for preprocess experiments
        self.set_property('no_props_file', True)

    def _prepare_translator_and_preprocessor(self, translator, preprocessor):
        # Copy the whole translate directory
        self.add_resource(translator.shell_name + '_DIR', translator.bin_dir,
                          translator.get_path_dest('translate'))
        # In order to set an environment variable, overwrite the executable
        self.add_resource(translator.shell_name,
                          translator.get_bin('translate.py'),
                          translator.get_path_dest('translate', 'translate.py'))
        self.add_resource(preprocessor.shell_name,
                          preprocessor.get_bin('preprocess'),
                          preprocessor.get_bin_dest())

    def _prepare_planner(self, planner):
        # Get the planner binary
        bin = None
        for name in PLANNER_BINARIES:
            path = os.path.join(planner.get_bin(name))
            if os.path.isfile(path):
                bin = path
                break
        if not bin:
            logging.error('None of the binaries %s could be found in %s' %
                          (PLANNER_BINARIES, planner.bin_dir))
            sys.exit(1)
        self.add_resource(planner.shell_name, bin, planner.get_bin_dest())
        for bin in PLANNER_HELPERS:
            src_path = planner.get_bin(bin)
            if not os.path.isfile(src_path):
                logging.warning('File %s could not be found. Is it required?' %
                                src_path)
                continue
            self.add_resource('NONAME', src_path, planner.get_path_dest(bin))

        # Find all portfolios and copy them into the experiment directory
        for portfolio in [name for name in self.config_nicks if name.endswith('.py')]:
            if not os.path.isfile(portfolio):
                logging.error('Portfolio file %s could not be found.' % portfolio)
                sys.exit(1)
            shell_name = shell_escape(os.path.basename(portfolio))
            self.add_resource(shell_name, portfolio, planner.get_path_dest(os.path.basename(portfolio)))

        # The tip changeset has the newest validator version so we use this one
        validate = os.path.join(tools.SCRIPTS_DIR, '..', 'src', 'validate')
        if not os.path.exists(validate):
            logging.error('Please run ./build_all in the src directory first '
                          'to compile the validator')
            sys.exit(1)
        self.add_resource('VALIDATE', validate, 'validate')

        downward_validate = os.path.join(tools.SCRIPTS_DIR, 'downward-validate.py')
        self.add_resource('DOWNWARD_VALIDATE', downward_validate, 'downward-validate')

    def make_runs(self):
        # Save the experiment stage in the properties
        if self.complete:
            self.set_property('stage', 'complete')
            self._make_complete_runs()
        elif self.preprocess:
            self.set_property('stage', 'preprocess')
            self._prepare_preprocess()
            self._make_preprocess_runs()
        else:
            self.set_property('stage', 'search')
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

            for config_nick, config in self.configs:
                for prob in self.problems:
                    self._make_search_run(translator, preprocessor, planner,
                                          config_nick, config, prob)

    def _make_search_run(self, translator, preprocessor, planner, config_nick,
                         config, prob):
        preprocess_dir = os.path.join(PREPROCESSED_TASKS_DIR,
                                      translator.name + '-' + preprocessor.name,
                                      prob.domain, prob.problem)
        def path(filename):
            return os.path.join(preprocess_dir, filename)

        run = DownwardRun(self, translator, preprocessor, planner, prob)
        self.add_run(run)

        run.set_property('preprocess_dir', preprocess_dir)

        run.set_property('compact', self.compact)
        sym = self.compact

        _prepare_search_run(self, run, config_nick, config)

        # Add the preprocess files for later parsing
        run.add_resource('OUTPUT', path('output'), 'output', symlink=sym)
        run.add_resource('ALL_GROUPS', path('all.groups'), 'all.groups', symlink=sym, required=False)
        run.add_resource('TEST_GROUPS', path('test.groups'), 'test.groups', symlink=sym, required=False)
        run.add_resource('OUTPUT_SAS', path('output.sas'), 'output.sas', symlink=sym)
        run.add_resource('DOMAIN', path('domain.pddl'), 'domain.pddl', symlink=sym)
        run.add_resource('PROBLEM', path('problem.pddl'), 'problem.pddl', symlink=sym)
        run.add_resource('PREPROCESS_PROPERTIES', path('properties'),
                         'preprocess-properties', symlink=sym)

        # The logs have to be copied, not linked
        run.add_resource('RUN_LOG', path('run.log'), 'run.log')
        run.add_resource('RUN_ERR', path('run.err'), 'run.err')

    def _make_complete_runs(self):
        for translator, preprocessor, planner in self.combinations:
            self._prepare_translator_and_preprocessor(translator, preprocessor)
            self._prepare_planner(planner)

            for config_nick, config in self.configs:
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
    combinations = [(checkouts.Translator(rev='WORK'),
                     checkouts.Preprocessor(rev='WORK'),
                     checkouts.Planner(rev='WORK'))]

    build_experiment(combinations)
