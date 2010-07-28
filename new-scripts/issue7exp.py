import os
import sys
#sys.path.insert(0, '../')

import planning
import experiments
import planning_suites

issue7_dir = 'issue7'



def build_planning_exp():
    exp = experiments.build_experiment(parser=planning.PlanningExpOptionParser())

    if not exp.configurations:
        exp.parser.error('You need to specify at least one configuration')
    if not exp.suite:
        exp.parser.error('You need to specify at least one suite')

    exp.add_resource("PLANNER", os.path.join(issue7_dir, 'trunk-r3842', 'downward/search/release-search'),
                    "release-search")
                    
               
    problems = planning_suites.build_suite(exp.suite)
    
    translator_revs = [3827, 3829, 3840, 4283]
    
    for translator_rev in translator_revs:
        translator = os.path.join(issue7_dir, 'translate-r%d' % translator_rev, 'translate.py')
        assert os.path.exists(translator)
        for config in exp.configurations:
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
    exp = build_planning_exp()
    exp.build()
