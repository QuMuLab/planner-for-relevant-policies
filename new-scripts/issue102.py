#! /usr/bin/env python
import os
import sys
import subprocess

import experiments
import downward_suites
import downward_configs as configs

main_dir = 'issue102'

PLANNER_URL = 'svn+ssh://downward/trunk/downward/search'

optimizations = ['O0', 'O1', 'O2', 'O3', 'Os']

configs =   [   ('ou', configs.ou),
                ('lama', configs.lama),
                ('blind', configs.blind),
                ('oa50000', configs.oa50000),
                ('yY', configs.yY),
                ('fF', configs.fF)
            ]
            
def make_reports():
    cmd = """\
./downward-reports.py issue102-STRIPS-eval/ \
-a score_search_time score_total_time search_time total_time \
--format html -c O0-blind O1-blind O2-blind O3-blind Os-blind"""
    for config_name, config in configs:
        new_cmd = cmd.replace('blind', config_name)
        new_cmd = new_cmd.split()
        subprocess.call(new_cmd)
    

def setup():
    cwd = os.getcwd()
    if not os.path.exists(main_dir):
        os.mkdir(main_dir)
    os.chdir(main_dir)
    
    if not os.path.exists('planner.cc'):
        cmd = ('svn co %s .' % PLANNER_URL).split()
        ret = subprocess.call(cmd)
    
    makefile_path = 'Makefile'
    makefile = open(makefile_path).read()
    
    for opt in optimizations:
        planner_name = 'downward-' + opt
        new_make = makefile.replace('-O3', '-'+opt)
        new_make = new_make.replace('TARGET  = downward', 'TARGET  = ' + planner_name)
        makefile_name = 'Makefile-' + opt
        with open(makefile_name, 'w') as file:
            file.write(new_make)
        
        if not os.path.exists(planner_name):
            # Needs compiling
            subprocess.call(['make', '-f', makefile_name])
                
    os.chdir(cwd)




def build_planning_exp():
    parser=experiments.ExpArgParser()
    parser.add_argument("-s", "--suite", default=[], required=True,
                        nargs='+', help="tasks, domains or suites")
    
    exp = experiments.build_experiment(parser)
            
    problems = downward_suites.build_suite(exp.suite)
    
    for opt in optimizations:
        planner_name = 'downward-' + opt
        planner = os.path.join(main_dir, planner_name)
        planner_var = 'PLANNER_' + opt
        exp.add_resource(planner_var, planner, planner_name)
        
        for config_name, config in configs:
            for problem in problems:
                run = exp.add_run()
                run.require_resource(planner_var)
                
                domain_file = problem.domain_file()
                problem_file = problem.problem_file()
                run.add_resource("DOMAIN", domain_file, "domain.pddl")
                run.add_resource("PROBLEM", problem_file, "problem.pddl")
                
                translator_path = os.path.abspath('../downward/translate/translate.py')
                assert os.path.exists(translator_path)
                translate_cmd = '%s %s %s' % (translator_path, domain_file, problem_file)
                
                preprocessor_path = '../downward/preprocess/preprocess'
                preprocessor_path = os.path.abspath(preprocessor_path)
                assert os.path.exists(preprocessor_path)
                preprocess_cmd = '%s < %s' % (preprocessor_path, 'output.sas')
                
                run.set_preprocess('%s; %s' % (translate_cmd, preprocess_cmd))
                
                run.set_command("$%s %s < output" % (planner_var, config))
                
                run.declare_optional_output("*.groups")
                run.declare_optional_output("output")
                run.declare_optional_output("output.sas")
                run.declare_optional_output("sas_plan")
                
                ext_config = opt + '-' + config_name
                
                run.set_property('opt', opt)
                run.set_property('config', ext_config)
                run.set_property('domain', problem.domain)
                run.set_property('problem', problem.problem)
                run.set_property('id', [ext_config, problem.domain, problem.problem])
            
    return exp

if __name__ == '__main__':
    if 'report' in sys.argv:
        make_reports()
        sys.exit()
    setup()
    exp = build_planning_exp()
    exp.build()
