#! /usr/bin/env python

from downward_experiments import *
import experiments


def build_translator_experiment(translators,
                                parser=experiments.ExpArgParser()):
    parser.add_argument('-s', '--suite', default=[], nargs='+',
                            required=True, help=downward_suites.HELP)
    exp = experiments.build_experiment(parser)
    
    # Use unique name for the translator experiment
    if not exp.name.endswith('-t'):
        exp.name += '-t'
        logging.info('Experiment name set to %s' % exp.name)

    # Use unique dir for the translator experiment
    if not exp.base_dir.endswith('-t'):
        exp.base_dir += '-t'
        logging.info('Experiment directory set to %s' % exp.base_dir)

    # Set defaults for faster preprocessing
    #exp.suite = ['ALL']
    exp.runs_per_task = 8
    logging.info('GkiGrid experiments: runs per task set to %s' % exp.runs_per_task)
    import multiprocessing
    exp.processes = multiprocessing.cpu_count()
    logging.info('Local experiments: processes set to %s' % exp.processes)
    
    # We need the "output" file, not only the properties file
    exp.set_property('copy_all', True)
   
    for translator in translators:
        translator.checkout()
    
    problems = downward_suites.build_suite(exp.suite)
   
    for trans in translators:
        translator = trans.get_executable()
        assert os.path.exists(translator), translator
        
        for problem in problems:
            run = exp.add_run()
            domain_file = problem.domain_file()
            problem_file = problem.problem_file()
            run.add_resource("DOMAIN", domain_file, "domain.pddl")
            run.add_resource("PROBLEM", problem_file, "problem.pddl")
            run.set_property('translator', trans.rev)
            run.set_property('translator_parent', trans.parent_rev)
            run.set_property('config', trans.rev)
            run.set_property('domain', problem.domain)
            run.set_property('problem', problem.problem)
            run.set_property('id', [trans.rev, problem.domain, problem.problem])
            translate_cmd = 'set -e; %s %s %s' % (translator, problem.domain,
                                                  problem.problem)
            run.set_command(translate_cmd)
    exp.build()


old_rev = '213202a44ebe'
new_rev = '7bc6764d4116'

old_translator = TranslatorHgCheckout(rev=old_rev)
new_translator = TranslatorHgCheckout(rev=new_rev)

build_translator_experiment([old_translator, new_translator])
