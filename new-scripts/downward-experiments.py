#! /usr/bin/env python
"""
Module that permits the generation of planning experiments

Use either by invoking the module directly or using the build_planning_exp() 
function from another another module for further customization
"""

import os
import sys

import experiments
import planning_suites
        
        

def build_planning_exp():
    parser = experiments.ExpArgParser()
    parser.add_argument('-c', '--configs', default=[], 
                        nargs='+', help='planner configurations')
    parser.add_argument('-s', '--suite', default=[], nargs='+',
                        help='tasks, domains or suites')
    
    exp = experiments.build_experiment(parser)

    exp.add_resource('PLANNER', '../downward/search/downward',
                    'downward')
                    
               
    problems = planning_suites.build_suite(exp.suite)

    for config in exp.configs:
        for problem in problems:
            run = exp.add_run()
            run.require_resource('PLANNER')
            
            domain_file = problem.domain_file()
            problem_file = problem.problem_file()
            run.add_resource('DOMAIN', domain_file, 'domain.pddl')
            run.add_resource('PROBLEM', problem_file, 'problem.pddl')
            
            translator_path = '../downward/translate/translate.py'
            translator_path = os.path.abspath(translator_path)
            translate_cmd = '%s %s %s' % (translator_path, domain_file, problem_file)
            
            preprocessor_path = '../downward/preprocess/preprocess'
            preprocessor_path = os.path.abspath(preprocessor_path)
            preprocess_cmd = '%s < %s' % (preprocessor_path, 'output.sas')
            
            run.set_preprocess('%s; %s' % (translate_cmd, preprocess_cmd))
            
            run.set_command("$PLANNER --search 'lazy(single(%s))' < output" % config)
            
            run.declare_optional_output('*.groups')
            run.declare_optional_output('output')
            run.declare_optional_output('output.sas')
            run.declare_optional_output('sas_plan')
            
            run.set_property('config', config)
            run.set_property('domain', problem.domain)
            run.set_property('problem', problem.problem)
            run.set_property('id', [config, problem.domain, problem.problem])
            
    return exp


if __name__ == '__main__':
    exp = build_planning_exp()
    exp.build()





