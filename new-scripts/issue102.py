#! /usr/bin/env python
import os
import sys
import subprocess

import experiments
import downward_suites
import downward_configs
import tools
from downward_experiments import TranslatorHgCheckout, PreprocessorHgCheckout, \
                                    PlannerHgCheckout, make_checkouts, _get_configs

optimizations = ['O0', 'O1', 'O2', 'O3', 'Os']

#configs =   [   ('ou', configs.ou),
#                ('lama', configs.lama),
#                ('blind', configs.blind),
#                ('oa50000', configs.oa50000),
#                ('yY', configs.yY),
#                ('fF', configs.fF),
#            ]


def build_complete_experiment(combinations, parser=experiments.ExpArgParser()):
    parser.add_argument('-s', '--suite', default=[], nargs='+', 
                            required=True, help=downward_suites.HELP)
    parser.add_argument('-c', '--configs', default=[], nargs='+', 
                            required=True, help=downward_configs.HELP)
                            
    exp = experiments.build_experiment(parser)
    
    make_checkouts(combinations)
            
    problems = downward_suites.build_suite(exp.suite)
    
    for translator_co, preprocessor_co, planner_co in combinations:
        
        translator = translator_co.get_executable()
        assert os.path.exists(translator), translator
        
        preprocessor = preprocessor_co.get_executable()
        assert os.path.exists(preprocessor)
        preprocessor_name = "PREPROCESSOR_%s" % preprocessor_co.rev
        exp.add_resource(preprocessor_name, preprocessor, preprocessor_co.name)
        
        planner = planner_co.get_executable()
        assert os.path.exists(planner), planner
        opt = os.path.basename(planner).split('-')[1]
        planner_name = "PLANNER_%s_%s" % (planner_co.rev, opt)
        exp.add_resource(planner_name, planner, planner_co.name)
        
        configs = _get_configs(planner_co.rev, exp.configs)
         
        for config_name, config in configs:
            for problem in problems:
                run = exp.add_run()
                run.require_resource(preprocessor_name)
                run.require_resource(planner_name)
                
                domain_file = problem.domain_file()
                problem_file = problem.problem_file()
                run.add_resource("DOMAIN", domain_file, "domain.pddl")
                run.add_resource("PROBLEM", problem_file, "problem.pddl")
                
                translator = os.path.abspath(translator)
                translate_cmd = '%s %s %s' % (translator, domain_file, 
                                                problem_file)
                
                preprocess_cmd = '$%s < %s' % (preprocessor_name, 'output.sas')
                
                run.set_preprocess('%s; %s' % (translate_cmd, preprocess_cmd))
                
                run.set_command("$%s %s < output" % (planner_name, config))
                
                run.declare_optional_output("*.groups")
                run.declare_optional_output("output")
                run.declare_optional_output("output.sas")
                run.declare_optional_output("sas_plan")
                
                ext_config = '-'.join([opt, translator_co.rev, preprocessor_co.rev, 
                                        planner_co.rev, config_name])
                                        
                run.set_property('opt', opt)
                
                run.set_property('translator', translator_co.rev)
                run.set_property('preprocessor', preprocessor_co.rev)
                run.set_property('planner', planner_co.rev)
                
                run.set_property('commandline_config', config)
                
                run.set_property('config', ext_config)
                run.set_property('domain', problem.domain)
                run.set_property('problem', problem.problem)
                run.set_property('id', [ext_config, problem.domain, 
                                        problem.problem])
    exp.build()
    return exp

if __name__ == '__main__':
    translator = TranslatorHgCheckout()
    preprocessor = PreprocessorHgCheckout()
    
    combos = []
    for opt in optimizations:
        planner = PlannerHgCheckout(rev='f48caab7cb5f')
        planner.checkout_dir += '-' + opt
        print planner.checkout_dir
        planner.checkout()
        
        makefile_path = os.path.join(planner.exe_dir, 'Makefile')
        assert os.path.exists(makefile_path)
        makefile = open(makefile_path).read()
        
        planner_name = 'downward-' + opt
        new_make = makefile.replace('-O3', '-'+opt)
        new_make = new_make.replace('TARGET  = downward\n', 'TARGET  = ' + planner_name + '\n')
        planner.executable = os.path.join(planner.exe_dir, planner_name)
        import new
        planner.get_executable = new.instancemethod(lambda self: self.executable, planner, planner.__class__)
        with open(makefile_path, 'w') as file:
            file.write(new_make)
        
        combos.append((translator, preprocessor, planner))
    
    exp = build_complete_experiment(combos)
