#! /usr/bin/env python
import os
import sys

import experiments
import downward_suites
import downward_configs
import tools
from downward_experiments import (TranslatorHgCheckout, PreprocessorHgCheckout,
                               PlannerHgCheckout, make_checkouts, _get_configs)


def build_complete_experiment(combinations, parser=experiments.ExpArgParser()):
    parser.add_argument('-s', '--suite', default=[], type=tools.csv,
                            required=True, help=downward_suites.HELP)
    parser.add_argument('-c', '--configs', default=[], type=tools.csv,
                            required=True, help=downward_configs.HELP)

    exp = experiments.build_experiment(parser)

    make_checkouts([(trans, pre, plan) for trans, pre, plan, opt in combinations])

    problems = downward_suites.build_suite(exp.suite)

    # Pass opt directly
    for translator_co, preprocessor_co, planner_co, opt in combinations:

        translator = translator_co.get_executable()
        assert os.path.exists(translator), translator

        preprocessor = preprocessor_co.get_executable()
        assert os.path.exists(preprocessor)
        preprocessor_name = "PREPROCESSOR_%s" % preprocessor_co.rev
        exp.add_resource(preprocessor_name, preprocessor, preprocessor_co.name)

        planner = planner_co.get_executable()
        assert os.path.exists(planner), planner
        planner_name = "PLANNER_%s_%s" % (planner_co.rev, opt)
        planner_filename = "search-%s-%s" % (planner_co.rev, opt)
        exp.add_resource(planner_name, planner, planner_filename)

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


def build_makefile_experiment(settings, planner_rev='tip'):
    msg = 'We have to use a real checkout for changing the makefiles'
    assert not planner_rev.upper() == 'WORK', msg

    translator = TranslatorHgCheckout()
    preprocessor = PreprocessorHgCheckout()

    combos = []
    for name, replacements in settings:
        planner = PlannerHgCheckout(rev=planner_rev)
        planner.checkout_dir += '-' + name
        print planner.checkout_dir
        planner.checkout()

        makefile_path = os.path.join(planner.exe_dir, 'Makefile')
        assert os.path.exists(makefile_path)
        makefile = open(makefile_path).read()

        new_make = makefile
        planner_name = 'downward-' + name
        for orig, replacement in replacements:
            new_make = new_make.replace(orig, replacement)
        old_target = 'TARGET  = downward\n'
        new_target = 'TARGET  = ' + planner_name + '\n'
        new_make = new_make.replace(old_target, new_target)

        planner.executable = os.path.join(planner.exe_dir, planner_name)
        import new
        method = [lambda self: self.executable, planner, planner.__class__]
        planner.get_executable = new.instancemethod(*method)
        with open(makefile_path, 'w') as file:
            file.write(new_make)

        combos.append((translator, preprocessor, planner, name))

    build_complete_experiment(combos)


def compare_assertions():
    settings = [
        ('nopoint_noassert', []),
        ('point_noassert', [('-fomit-frame-pointer', '')]),
        ('nopoint_assert', [('-DNDEBUG', '')]),
        ('point_assert', [('-fomit-frame-pointer', ''), ('-DNDEBUG', '')]),
        ]
    build_makefile_experiment(settings)


def compare_optimizations():
    optimizations = ['O0', 'O1', 'O2', 'O3', 'Os']
    settings = [(opt, [('-O3', '-' + opt)]) for opt in optimizations]
    build_makefile_experiment(settings)


if __name__ == '__main__':
    if 'opt' in sys.argv:
        sys.argv.remove('opt')
        compare_optimizations()
    elif 'assert' in sys.argv:
        sys.argv.remove('assert')
        compare_assertions()
    else:
        print 'Add "opt" or "assert" on the commandline to choose a test'
