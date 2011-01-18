#! /usr/bin/env python
"""
A module that has methods for checking out different revisions of the three
components of fast-downward (translate, preprocess, search) and performing
experiments with them.
"""
import os
import sys
import subprocess
import logging
import re

import experiments
import downward_suites
import downward_configs
import tools

SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '../'))
CHECKOUTS_DIRNAME = 'checkouts'
CHECKOUTS_DIR = os.path.join(SCRIPTS_DIR, CHECKOUTS_DIRNAME)
if not os.path.exists(CHECKOUTS_DIR):
    os.mkdir(CHECKOUTS_DIR)

PREPROCESSED_TASKS_DIR = os.path.join(SCRIPTS_DIR, 'preprocessed-tasks')
if not os.path.exists(PREPROCESSED_TASKS_DIR):
    os.mkdir(PREPROCESSED_TASKS_DIR)

BASE_DIR = os.path.abspath(os.path.join(SCRIPTS_DIR, '../'))


ABS_REV_CACHE = {}
_sentinel = object()


class Checkout(object):
    def __init__(self, part, repo, rev, checkout_dir, name):
        # Directory name of the planner part (translate, preprocess, search)
        self.part = part
        self.repo = repo
        self.rev = str(rev)
        # Nickname for the checkout (used for reports and checkout directory)
        self.name = name

        if not os.path.isabs(checkout_dir):
            checkout_dir = os.path.join(CHECKOUTS_DIR, checkout_dir)
        self.checkout_dir = os.path.abspath(checkout_dir)

        self._executable = None

    def checkout(self):
        # We don't need to check out the working copy
        if not self.rev == 'WORK':
            # If there's already a checkout, don't checkout again
            path = self.checkout_dir
            if os.path.exists(path):
                logging.debug('Checkout "%s" already exists' % path)
            else:
                cmd = self.get_checkout_cmd()
                print cmd
                ret = subprocess.call(cmd, shell=True)
            assert os.path.exists(path), \
                    'Could not checkout to "%s"' % path

    def get_checkout_cmd(self):
        raise Exception('Not implemented')

    def compile(self):
        """
        We need to compile the code if the executable does not exist.
        Additionally we want to compile it, when we run an experiment with
        the working copy to make sure the executable is based on the latest
        version of the code. Obviously we don't need no compile the
        translator code.
        """
        if self.part == 'translate':
            return

        if self.rev == 'WORK' or self._get_executable(default=None) is None:
            cwd = os.getcwd()
            src_dir = os.path.dirname(self.exe_dir)
            os.chdir(src_dir)
            subprocess.call(['./build_all'])
            os.chdir(cwd)

    def _get_executable(self, default=_sentinel):
        """ Returns the path to the python module or a binary """
        names = ['translate.py', 'preprocess',
                'downward', 'release-search', 'search',
                'downward-debug', 'downward-profile']
        for name in names:
            planner = os.path.join(self.exe_dir, name)
            if os.path.exists(planner):
                return planner
        if default is _sentinel:
            logging.error('%s executable could not be found in %s' %
                            (self.part, self.exe_dir))
            sys.exit(1)
        return default

    @property
    def binary(self):
        if not self._executable:
            self._executable = self._get_executable()
        return self._executable

    @property
    def parent_rev(self):
        raise Exception('Not implemented')

    @property
    def exe_dir(self):
        raise Exception('Not implemented')

    @property
    def rel_dest(self):
        return 'code-%s/%s' % (self.rev, self.part)

    @property
    def shell_name(self):
        return '%s_%s' % (self.part.upper(), self.rev)


# ---------- Mercurial ---------------------------------------------------------

class HgCheckout(Checkout):
    DEFAULT_URL = BASE_DIR # was 'ssh://downward'
    DEFAULT_REV = 'WORK'

    def __init__(self, part, repo=DEFAULT_URL, rev=DEFAULT_REV, name=''):
        rev_nick = str(rev).upper()
        # Find proper absolute revision
        rev_abs = self.get_rev_abs(repo, rev)

        if rev_nick == 'WORK':
            checkout_dir = os.path.join(SCRIPTS_DIR, '../')
        else:
            checkout_dir = name if name else rev_abs

        if not name:
            name = part + '-' + rev_nick

        Checkout.__init__(self, part, repo, rev_abs, checkout_dir, name)
        self.parent = None

    def get_rev_abs(self, repo, rev):
        if str(rev).upper() == 'WORK':
            return 'WORK'
        cmd = 'hg id -ir %s %s' % (str(rev).lower(), repo)
        if cmd in ABS_REV_CACHE:
            return ABS_REV_CACHE[cmd]
        abs_rev = tools.run_command(cmd)
        if not abs_rev:
            logging.error('Revision %s is not present in repo %s' % (rev, repo))
            sys.exit(1)
        ABS_REV_CACHE[cmd] = abs_rev
        return abs_rev

    def get_checkout_cmd(self):
        cwd = os.getcwd()
        clone = 'hg clone -r %s %s %s' % (self.rev, self.repo, self.checkout_dir)
        cd_to_repo_dir = 'cd %s' % self.checkout_dir
        update = 'hg update -r %s' % self.rev
        cd_back = 'cd %s' % cwd
        return '; '.join([clone, cd_to_repo_dir, update, cd_back])

    @property
    def parent_rev(self):
        if self.parent:
            return self.parent
        rev = self.rev
        if self.rev == 'WORK':
            rev = 'tip'
        cmd = 'hg log -r %s --template {node|short}' % rev
        self.parent = tools.run_command(cmd)
        return self.parent

    @property
    def exe_dir(self):
        assert os.path.exists(self.checkout_dir), self.checkout_dir
        exe_dir = os.path.join(self.checkout_dir, 'downward', self.part)
        # "downward" dir has been renamed to "src"
        if not os.path.exists(exe_dir):
            exe_dir = os.path.join(self.checkout_dir, 'src', self.part)
        return exe_dir


class TranslatorHgCheckout(HgCheckout):
    def __init__(self, *args, **kwargs):
        HgCheckout.__init__(self, 'translate', *args, **kwargs)

class PreprocessorHgCheckout(HgCheckout):
    def __init__(self, *args, **kwargs):
        HgCheckout.__init__(self, 'preprocess', *args, **kwargs)

class PlannerHgCheckout(HgCheckout):
    def __init__(self, *args, **kwargs):
        HgCheckout.__init__(self, 'search', *args, **kwargs)



# ---------- Subversion --------------------------------------------------------

class SvnCheckout(Checkout):
    DEFAULT_URL = 'svn+ssh://downward-svn/trunk/downward'
    DEFAULT_REV = 'WORK'

    REV_REGEX = re.compile(r'Revision: (\d+)')

    def __init__(self, part, repo, rev=DEFAULT_REV):
        rev = str(rev)
        name = part + '-' + rev
        rev_abs = self.get_rev_abs(repo, rev)

        if rev == 'WORK':
            logging.error('Comparing SVN working copy is not supported')
            sys.exit(1)

        checkout_dir = part + '-' + rev_abs

        Checkout.__init__(self, part, repo, rev_abs, checkout_dir, name)

    def get_rev_abs(self, repo, rev):
        try:
            rev_number = int(rev)
            return rev
        except ValueError:
            pass

        if rev.upper() == 'WORK':
            return 'WORK'
        elif rev.upper() == 'HEAD':
            # We want the HEAD revision number
            return self._get_rev(repo)
        else:
            logging.error('Invalid SVN revision specified: %s' % rev)
            sys.exit()

    def _get_rev(self, repo):
        """
        Returns the revision for the given repo. If the repo is a remote URL,
        the HEAD revision is returned. If the repo is a local path, the
        working copy's version is returned.
        """
        env = {'LANG': 'C'}
        cmd = 'svn info %s' % repo
        if cmd in ABS_REV_CACHE:
            return ABS_REV_CACHE[cmd]
        output = tools.run_command(cmd, env=env)
        match = self.REV_REGEX.search(output)
        if not match:
            logging.error('Unable to get HEAD revision number')
            sys.exit()
        rev_number = match.group(1)
        ABS_REV_CACHE[cmd] = rev_number
        return rev_number

    def get_checkout_cmd(self):
        return 'svn co %s@%s %s' % (self.repo, self.rev, self.checkout_dir)

    @property
    def parent_rev(self):
        return self._get_rev(self.checkout_dir)

    @property
    def exe_dir(self):
        # checkout_dir is exe_dir for SVN
        assert os.path.exists(self.checkout_dir)
        return self.checkout_dir


class TranslatorSvnCheckout(SvnCheckout):
    DEFAULT_URL = 'svn+ssh://downward-svn/trunk/downward/translate'

    def __init__(self, repo=DEFAULT_URL, rev=SvnCheckout.DEFAULT_REV):
        SvnCheckout.__init__(self, 'translate', repo, rev)


class PreprocessorSvnCheckout(SvnCheckout):
    DEFAULT_URL = 'svn+ssh://downward-svn/trunk/downward/preprocess'

    def __init__(self, repo=DEFAULT_URL, rev=SvnCheckout.DEFAULT_REV):
        SvnCheckout.__init__(self, 'preprocess', repo, rev)


class PlannerSvnCheckout(SvnCheckout):
    DEFAULT_URL = 'svn+ssh://downward-svn/trunk/downward/search'

    def __init__(self, repo=DEFAULT_URL, rev=SvnCheckout.DEFAULT_REV):
        SvnCheckout.__init__(self, 'search', repo, rev)

# ------------------------------------------------------------------------------


def make_checkouts(combinations):
    """
    Checks out and compiles the code
    We allow both lists of checkouts and list of checkout tuples
    """
    parts = []

    for combo in combinations:
        if isinstance(combo, Checkout):
            parts.append(combo)
        else:
            for part in combo:
                parts.append(part)

    for part in parts:
        part.checkout()
        part.compile()


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


def _require_checkout(exp, part):
    exp.add_resource(part.shell_name, part.binary, part.rel_dest)


def _get_preprocess_cmd(translator, preprocessor):
    translate_cmd = '$%s $DOMAIN $PROBLEM' % translator.shell_name
    preprocess_cmd = '$%s < output.sas' % preprocessor.shell_name
    return 'set -e; %s; %s' % (translate_cmd, preprocess_cmd)


def _prepare_run(exp, run, problem, translator, preprocessor):
    run.set_property('translator', translator.rev)
    run.set_property('preprocessor', preprocessor.rev)

    run.set_property('translator_parent', translator.parent_rev)
    run.set_property('preprocessor_parent', preprocessor.parent_rev)

    run.set_property('domain', problem.domain)
    run.set_property('problem', problem.problem)

    # Set memory limit in KB
    run.set_property('memory_limit', exp.memory * 1024)


def _prepare_preprocess_run(run, problem, translator, preprocessor):
    """
    This method adds the necessary preprocessing information to a run.
    Nothing is returned, all changes to the run are side effects
    """
    run.require_resource(preprocessor.shell_name)

    domain_file = problem.domain_file()
    problem_file = problem.problem_file()
    run.add_resource("DOMAIN", domain_file, "domain.pddl")
    run.add_resource("PROBLEM", problem_file, "problem.pddl")

    run.set_command(_get_preprocess_cmd(translator, preprocessor))

    run.declare_optional_output("*.groups")
    run.declare_optional_output("output.sas")
    run.declare_optional_output("output")

    ext_config = '-'.join([translator.rev, preprocessor.rev])

    run.set_property('config', ext_config)
    run.set_property('id', [ext_config, problem.domain, problem.problem])


def _prepare_search_run(run, problem, translator, preprocessor,
                        planner, config, config_name):
    run.require_resource(planner.shell_name)

    run.set_command("$%s %s < $OUTPUT" % (planner.shell_name, config))

    run.declare_optional_output("sas_plan")

    # If all three parts have the same revision don't clutter the reports
    if translator.rev == preprocessor.rev and translator.rev == planner.rev:
        revs = [translator.rev]
    else:
        revs = [translator.rev, preprocessor.rev, planner.rev]
    ext_config = '-'.join(revs + [config_name])

    run.set_property('planner', planner.rev)
    run.set_property('planner_parent', planner.parent_rev)

    run.set_property('commandline_config', config)

    run.set_property('config', ext_config)
    run.set_property('id', [ext_config, problem.domain, problem.problem])


def _prepare_preprocess_exp(exp, translator, preprocessor):
    # Copy the whole translate directory
    exp.add_resource(translator.shell_name + '_DIR', translator.exe_dir,
                     translator.rel_dest)
    # In order to set an environment variable, overwrite the executable
    exp.add_resource(translator.shell_name,
                     os.path.join(translator.exe_dir, 'translate.py'),
                     os.path.join(translator.rel_dest, 'translate.py'))
    _require_checkout(exp, preprocessor)


def _prepare_search_exp(exp, translator, preprocessor, planner):
    _require_checkout(exp, planner)
    for bin in ['downward-1', 'downward-2', 'downward-4', 'dispatch']:
        src_path = os.path.join(planner.exe_dir, bin)
        if not os.path.isfile(src_path):
            continue
        code_subdir = os.path.dirname(planner.rel_dest)
        exp.add_resource('DOWNWARD1', src_path,
                        os.path.join(code_subdir, bin))


def build_preprocess_exp(combinations, parser=experiments.ExpArgParser()):
    """
    When the option --preprocess is passed on the commandline this method
    is invoked an creates a preprocessing experiment.

    When the resultfetcher is run the following directory structure is created:

    SCRIPTS_DIR
        - preprocessed-tasks
            - TRANSLATOR_REV-PREPROCESSOR_REV
                - DOMAIN
                    - PROBLEM
                        - output
    """
    exp = experiments.build_experiment(parser)

    # Use unique name for the preprocess experiment
    if not exp.name.endswith('-p'):
        exp.name += '-p'
        logging.info('Experiment name set to %s' % exp.name)

    # Use unique dir for the preprocess experiment
    if not exp.base_dir.endswith('-p'):
        exp.base_dir += '-p'
        logging.info('Experiment directory set to %s' % exp.base_dir)

    # Add some instructions
    if type(exp) == experiments.LocalExperiment:
        exp.end_instructions = 'Preprocess experiment has been created. ' \
            'Before you can create the search experiment you have to run\n' \
            './%(exp_name)s/run\n' \
            './resultfetcher.py %(exp_name)s' % {'exp_name': exp.name}
    elif type(exp) == experiments.GkiGridExperiment:
        exp.end_instructions = 'You can submit the preprocessing ' \
            'experiment to the queue now by calling ' \
            '"qsub ./%(name)s/%(filename)s"' % exp.__dict__

    # Set the eval directory already here, we don't want the results to land
    # in the default testname-eval
    exp.set_property('eval_dir', PREPROCESSED_TASKS_DIR)

    # We need the "output" file, not only the properties file
    exp.set_property('copy_all', True)

    make_checkouts(combinations)

    problems = downward_suites.build_suite(exp.suite)

    for combo in combinations:
        # Omit a possible search checkout
        translator, preprocessor = combo[:2]

        _prepare_preprocess_exp(exp, translator, preprocessor)

        for problem in problems:
            run = exp.add_run()
            _prepare_run(exp, run, problem, translator, preprocessor)
            _prepare_preprocess_run(run, problem, translator, preprocessor)
    exp.build()



def build_search_exp(combinations, parser=experiments.ExpArgParser()):
    """
    combinations can either be a list of PlannerCheckouts or a list of tuples
    (translator, preprocessor, planner)

    In the first case we fill the list with Translate and Preprocessor
    "Checkouts" that use the working copy code
    """
    exp = experiments.build_experiment(parser)

    make_checkouts(combinations)

    problems = downward_suites.build_suite(exp.suite)

    experiment_combos = []

    for combo in combinations:

        if isinstance(combo, Checkout):
            planner = combo
            assert planner.part == 'search'
            translator = TranslatorHgCheckout(rev='WORK')
            preprocessor = PreprocessorHgCheckout(rev='WORK')
        else:
            assert len(combo) == 3
            translator, preprocessor, planner = combo
            assert translator.part == 'translate'
            assert preprocessor.part == 'preprocess'
            assert planner.part == 'search'

        experiment_combos.append((translator, preprocessor, planner))

    for translator, preprocessor, planner in experiment_combos:
        _prepare_search_exp(exp, translator, preprocessor, planner)

        configs = _get_configs(planner.rev, exp.configs)

        for config_name, config in configs:
            for problem in problems:
                run = exp.add_run()
                _prepare_run(exp, run, problem, translator, preprocessor)
                _prepare_search_run(run, problem, translator, preprocessor,
                                planner, config, config_name)

                tasks_dir = PREPROCESSED_TASKS_DIR
                preprocess_version = translator.rev+'-'+preprocessor.rev
                preprocess_dir = os.path.join(tasks_dir, preprocess_version,
                                    problem.domain, problem.problem)
                output = os.path.join(preprocess_dir, 'output')
                # Add the preprocess files for later parsing
                test_groups = os.path.join(preprocess_dir, 'test.groups')
                all_groups = os.path.join(preprocess_dir, 'all.groups')
                output_sas = os.path.join(preprocess_dir, 'output.sas')
                run_log = os.path.join(preprocess_dir, 'run.log')
                run_err = os.path.join(preprocess_dir, 'run.err')
                domain_file = os.path.join(preprocess_dir, 'domain.pddl')
                problem_file = os.path.join(preprocess_dir, 'problem.pddl')
                #if not os.path.exists(output):
                #    msg = 'Preprocessed file not found at "%s". ' % output
                #    msg += 'Have you run the preprocessing experiment '
                #    msg += 'and ./resultfetcher.py ?'
                #    logging.warning(msg)
                run.add_resource('OUTPUT', output, 'output', required=False)
                run.add_resource('TEST_GROUPS', test_groups, 'test.groups',
                                 required=False)
                run.add_resource('ALL_GROUPS', all_groups, 'all.groups',
                                 required=False)
                run.add_resource('OUTPUT_SAS', output_sas, 'output.sas',
                                 required=False)
                run.add_resource('RUN_LOG', run_log, 'run.log')
                run.add_resource('RUN_ERR', run_err, 'run.err')
                run.add_resource('DOMAIN', domain_file, 'domain.pddl')
                run.add_resource('PROBLEM', problem_file, 'problem.pddl')
    exp.build()


def build_complete_experiment(combinations, parser=experiments.ExpArgParser()):
    exp = experiments.build_experiment(parser)

    make_checkouts(combinations)

    problems = downward_suites.build_suite(exp.suite)

    for translator, preprocessor, planner in combinations:
        _prepare_preprocess_exp(exp, translator, preprocessor)
        _prepare_search_exp(exp, translator, preprocessor, planner)

        configs = _get_configs(planner.rev, exp.configs)

        for config_name, config in configs:
            for problem in problems:
                run = exp.add_run()
                _prepare_run(exp, run, problem, translator, preprocessor)
                _prepare_preprocess_run(run, problem, translator, preprocessor)
                _prepare_search_run(run, problem, translator, preprocessor,
                                    planner, config, config_name)
                # We want to do the whole experiment in one step
                run.set_preprocess('')
                preprocess_cmd = _get_preprocess_cmd(translator, preprocessor)
                # There is no $OUTPUT variable in a "complete" experiment
                search_cmd = "$%s %s < output" % (planner.shell_name, config)
                run.set_command(preprocess_cmd + '; ' + search_cmd)
    exp.build()
    return exp


def test():
    combinations = [
        (TranslatorHgCheckout(), PreprocessorHgCheckout(rev='TIP'),
                                PlannerHgCheckout(rev='WORK')),
        (TranslatorSvnCheckout(), PreprocessorSvnCheckout(rev='head'),
                                PlannerSvnCheckout(rev='WORK')),
        (TranslatorSvnCheckout(rev=4321), PreprocessorHgCheckout(rev='tip'),
                                PlannerSvnCheckout(rev='HEAD')),
        (TranslatorHgCheckout(rev='a640c9a9284c'),
            PreprocessorHgCheckout(rev='work'), PlannerHgCheckout(rev='623')),
                   ]
    build_experiment(combinations)


def build_experiment(combinations):
    exp_type_parser = tools.ArgParser(add_help=False, add_log_option=False)
    exp_type_parser.add_argument('-p', '--preprocess', action='store_true',
                        default=False, help='build preprocessing experiment')
    exp_type_parser.add_argument('--complete', action='store_true',
                        default=False,
                        help='build complete experiment (overrides -p)')

    known_args, remaining_args = exp_type_parser.parse_known_args()
    # delete parsed args
    sys.argv = [sys.argv[0]] + remaining_args

    logging.info('Preprocess exp: %s' % known_args.preprocess)

    config_needed = known_args.complete or not known_args.preprocess

    parser = experiments.ExpArgParser(parents=[exp_type_parser])
    parser.add_argument('-s', '--suite', default=[], type=tools.csv,
                            required=True, help=downward_suites.HELP)
    parser.add_argument('-c', '--configs', default=[], type=tools.csv,
                            required=config_needed, help=downward_configs.HELP)

    if known_args.complete:
        build_complete_experiment(combinations, parser)
    elif known_args.preprocess:
        build_preprocess_exp(combinations, parser)
    else:
        build_search_exp(combinations, parser)


if __name__ == '__main__':
    combinations = [(TranslatorHgCheckout(rev='WORK'),
                    PreprocessorHgCheckout(rev='WORK'),
                    PlannerHgCheckout(rev='WORK'))]

    build_experiment(combinations)
