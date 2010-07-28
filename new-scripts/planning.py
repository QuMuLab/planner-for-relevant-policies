'''
Module that permits the generation of planning experiments

Use either by invoking the module directly or using the build_planning_exp() 
function from another another module for further customization
'''

import os
import sys

import experiments
import planning_suites


class PlanningExpArgParser(experiments.ExpArgParser):
    def __init__(self, *args, **kwargs):
        experiments.ExpArgParser.__init__(self, *args, **kwargs)
        
        self.add_argument(
            "-c", "--configs", dest="configurations", default=[], nargs='+',
            help="planner configurations")
        self.add_argument(
            "-s", "--suite", default=[], nargs='+',
            help="tasks, domains or suites")

def build_planning_exp():
    exp = experiments.build_experiment(parser=PlanningExpArgParser())

    if not exp.configurations:
        exp.parser.error('You need to specify at least one configuration')
    if not exp.suite:
        exp.parser.error('You need to specify at least one suite')

    exp.add_resource("PLANNER", "../downward/search/release-search",
                    "release-search")
                    
               
    problems = planning_suites.build_suite(exp.suite)

    for config in exp.configurations:
        for problem in problems:
            run = exp.add_run()
            run.require_resource("PLANNER")
            
            domain_file = problem.domain_file()
            problem_file = problem.problem_file()
            run.add_resource("DOMAIN", domain_file, "domain.pddl")
            run.add_resource("PROBLEM", problem_file, "problem.pddl")
            
            translator_path = '../downward/translate/translate.py'
            translator_path = os.path.abspath(translator_path)
            translate_cmd = '%s %s %s' % (translator_path, domain_file, problem_file)
            
            preprocessor_path = '../downward/preprocess/preprocess'
            preprocessor_path = os.path.abspath(preprocessor_path)
            preprocess_cmd = '%s < %s' % (preprocessor_path, 'output.sas')
            
            run.set_preprocess('%s; %s' % (translate_cmd, preprocess_cmd))
            
            run.set_command("$PLANNER --search 'lazy(single(%s))' < output" % config)
            
            run.declare_optional_output("*.groups")
            run.declare_optional_output("output")
            run.declare_optional_output("output.sas")
            run.declare_optional_output("sas_plan")
            
            run.set_property('config', config)
            run.set_property('domain', problem.domain)
            run.set_property('problem', problem.problem)
            run.set_property('id', [config, problem.domain, problem.problem])
            
    return exp

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print 'Testing'
        sys.argv.extend('test -c cea,ff -s MINITEST --timeout 1'.split())
    exp = build_planning_exp()
    exp.build()





