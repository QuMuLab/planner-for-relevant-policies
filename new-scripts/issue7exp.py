#! /usr/bin/env python
import os
import sys
#sys.path.insert(0, '../')
import subprocess

import planning
import experiments
import downward_suites

issue7_dir = 'issue7'

PLANNER_REV = 3842
PLANNER_URL = 'svn+ssh://downward/trunk'

TRANSLATOR_REVS = [3827, 3829, 3840, 4283]

TRANSLATE_URL = 'svn+ssh://downward/branches/translate-andrew/downward/translate'
TRANSLATE_ALT_URL = 'svn+ssh://downward/trunk/downward/translate'

def setup():
    cwd = os.getcwd()
    if not os.path.exists(issue7_dir):
        os.mkdir(issue7_dir)
    os.chdir(issue7_dir)
    
    planner_rev_path = 'trunk-r%d' % PLANNER_REV
    if not os.path.exists(planner_rev_path):
        cmd = ('svn co %s@%d %s' % (PLANNER_URL, PLANNER_REV, planner_rev_path)).split()
        ret = subprocess.call(cmd)
    
    # Needs compiling
    planner = os.path.join(planner_rev_path, 'downward', 'search', 'release-search')
    if os.path.exists(planner_rev_path) and not os.path.exists(planner):
        os.chdir(os.path.join(planner_rev_path, 'downward'))
        subprocess.call(['./build_all'])
        os.chdir('../../')
        
    for rev in TRANSLATOR_REVS:
        translate_path = 'translate-r%d' % rev
        if not os.path.exists(translate_path):
            cmd = ('svn co %s@%d %s' % (TRANSLATE_URL, rev, translate_path)).split()
            ret = subprocess.call(cmd)
            if not ret == 0:
                cmd = ('svn co %s@%d %s' % (TRANSLATE_ALT_URL, rev, translate_path)).split()
                ret = subprocess.call(cmd)
                
    os.chdir(cwd)




def build_planning_exp():
    parser=experiments.ExpArgParser()
    parser.add_argument("-c", "--configs", default=[], 
                        nargs='+', help="planner configurations")
    parser.add_argument("-s", "--suite", default=[], nargs='+',
                        help="tasks, domains or suites")
    
    exp = experiments.build_experiment(parser)

    exp.add_resource("PLANNER", os.path.join(issue7_dir, 'trunk-r3842', 'downward/search/release-search'),
                    "release-search")
                    
            
    problems = downward_suites.build_suite(exp.suite)
    
    
    
    for translator_rev in TRANSLATOR_REVS:
        translator = os.path.join(issue7_dir, 'translate-r%d' % translator_rev, 'translate.py')
        assert os.path.exists(translator)
        for config in exp.configs:
            for problem in problems:
                run = exp.add_run()
                run.require_resource("PLANNER")
                
                domain_file = problem.domain_file()
                problem_file = problem.problem_file()
                run.add_resource("DOMAIN", domain_file, "domain.pddl")
                run.add_resource("PROBLEM", problem_file, "problem.pddl")
                
                translator_path = os.path.abspath(translator)
                translate_cmd = '%s %s %s' % (translator_path, domain_file, problem_file)
                
                preprocessor_path = os.path.join(issue7_dir, 'trunk-r3842', 'downward/preprocess/preprocess')
                preprocessor_path = os.path.abspath(preprocessor_path)
                preprocess_cmd = '%s < %s' % (preprocessor_path, 'output.sas')
                
                run.set_preprocess('%s; %s' % (translate_cmd, preprocess_cmd))
                
                run.set_command("$PLANNER %s < output" % config)
                
                run.declare_optional_output("*.groups")
                run.declare_optional_output("output")
                run.declare_optional_output("output.sas")
                run.declare_optional_output("sas_plan")
                
                ext_config = str(translator_rev) + '-' + config
                
                run.set_property('translator', translator_rev)
                run.set_property('config', ext_config)
                run.set_property('domain', problem.domain)
                run.set_property('problem', problem.problem)
                run.set_property('id', [ext_config, problem.domain, problem.problem])
            
    return exp

if __name__ == '__main__':
    #sys.argv += '-n issue7exp -c yY -s TEST'.split()
    setup()
    exp = build_planning_exp()
    exp.build()
