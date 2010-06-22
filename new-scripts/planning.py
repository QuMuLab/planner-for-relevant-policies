import os

import experiments
import planning_suites


class PlanningExpOptionParser(experiments.ExpOptionParser):
    def __init__(self, *args, **kwargs):
        experiments.ExpOptionParser.__init__(self, *args, **kwargs)
        
        self.add_option(
            "-c", "--configs", action="extend", type="string",
            dest="configurations", default=[],
            help="comma-separated list of configurations")
        self.add_option(
            "-s", "--suite", action="extend", type="string", 
            dest="suite", default=[],
            help="comma-separated list of tasks, domains or suites")


exp = experiments.build_experiment(parser=PlanningExpOptionParser())

if not exp.configurations:
    exp.parser.error('You need to specify at least one configuration')
if not exp.suite:
    exp.parser.error('You need to specify at least one suite')

#exp.add_resource("TRANSLATOR", "../downward/translate/translate.py",
#                "translate")
exp.add_resource("PLANNER", "../downward/search/release-search",
                "release-search")
                
           
problems = planning_suites.build_suite(exp.suite)

for config in exp.configurations:
    for problem in problems:
        run = exp.add_run()
        #run.require_resource("TRANSLATOR")
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
        
        run.set_command("$PLANNER %s < output" % config)

exp.build()





