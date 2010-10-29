#! /usr/bin/env python
"""
A module that prepares experiments for preprocessing planning problems

When the resultfetcher is run the following directory structure is created:

SCRIPTS_DIR
    - preprocessed-tasks
        - TRANSLATOR_REV-PREPROCESSOR_REV
            - DOMAIN
                - PROBLEM
                    - output
"""
import os
import sys
import subprocess
import logging

import experiments
import downward_suites
import downward_configs
import downward_comparisons

# e.g. issue69.py -> issue69-checkouts
SCRIPTS_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '../'))
DOWNWARD_DIR = os.path.join(SCRIPTS_DIR, '../downward')



def build_preprocess_exp(combinations):
    parser = experiments.ExpArgParser()
    
    parser.add_argument('-s', '--suite', default=[], nargs='+', 
                        required=True, help=downward_suites.HELP)
    
    # Add for compatibility, not actually parsed
    parser.add_argument('-c', '--configs', default=[], nargs='*', 
                            required=False, help=downward_configs.HELP)
    
    exp = experiments.build_experiment(parser)
    
    # Set defaults for faster preprocessing
    #exp.suite = ['ALL']
    exp.runs_per_task = 10
    logging.info('GkiGrid experiments: runs per task set to %s' % exp.runs_per_task)
    import multiprocessing
    exp.processes = multiprocessing.cpu_count()
    logging.info('Local experiments: processes set to %s' % exp.processes)
    
    # Set the eval directory already here, we don't want the results to land
    # in the default testname-eval
    exp.set_property('eval_dir', PREPROCESSED_TASKS_DIR)
    
    # We need the "output" file, not only the properties file
    exp.set_property('copy_all', True)
    
    downward_comparisons.make_checkouts(combinations)
            
    problems = downward_suites.build_suite(exp.suite)
    
    for translator_co, preprocessor_co in combinations:
    
        translator = translator_co.get_executable()
        assert os.path.exists(translator), translator
        
        preprocessor = preprocessor_co.get_executable()
        assert os.path.exists(preprocessor)
        preprocessor_name = "PREPROCESSOR_%s" % preprocessor_co.rev
        exp.add_resource(preprocessor_name, preprocessor, preprocessor_co.name)
         
        for problem in problems:
            run = exp.add_run()
            run.require_resource(preprocessor_name)
            
            domain_file = problem.domain_file()
            problem_file = problem.problem_file()
            run.add_resource("DOMAIN", domain_file, "domain.pddl")
            run.add_resource("PROBLEM", problem_file, "problem.pddl")
            
            translator = os.path.abspath(translator)
            translate_cmd = '%s %s %s' % (translator, domain_file, problem_file)
            
            preprocess_cmd = '$%s < %s' % (preprocessor_name, 'output.sas')
            
            run.set_command('%s; %s' % (translate_cmd, preprocess_cmd))
            
            run.declare_optional_output("*.groups")
            run.declare_optional_output("output.sas")
            run.declare_optional_output("output")
            
            ext_config = '-'.join([translator_co.rev, preprocessor_co.rev])
            
            run.set_property('translator', translator_co.rev)
            run.set_property('preprocessor', preprocessor_co.rev)
            
            run.set_property('config', ext_config)
            run.set_property('domain', problem.domain)
            run.set_property('problem', problem.problem)
            run.set_property('id', [ext_config, problem.domain, problem.problem])
            
    exp.build()
    
    
def test():
    from downward_comparisons import TranslatorHgCheckout, PreprocessorHgCheckout, \
                                    TranslatorSvnCheckout, PreprocessorSvnCheckout
    combinations = [
        (TranslatorHgCheckout(), PreprocessorHgCheckout(rev='TIP')),
        (TranslatorSvnCheckout(), PreprocessorSvnCheckout(rev='head')),
        (TranslatorSvnCheckout(rev=4321), PreprocessorHgCheckout(rev='tip')),
        (TranslatorHgCheckout(rev='a640c9a9284c'), PreprocessorHgCheckout(rev='work')),
    ]
    build_preprocess_exp(combinations)
    

if __name__ == '__main__':
    # If the module is invoked as a script, preprocess the files with the 
    # translator and preprocessor of the working copy
    translator = downward_comparisons.TranslatorHgCheckout(rev='WORK')
    preprocessor = downward_comparisons.PreprocessorHgCheckout(rev='WORK')
    combinations = [(translator, preprocessor)]
    
    build_preprocess_exp(combinations)
