#! /usr/bin/env python
"""
A module to perform experiments with a planner packed as required
for IPC 2011. (does not suppprt zip)
"""
import os
import shutil
import sys
import subprocess
import tarfile

import experiments
import downward_suites
import tools

def reuse_planner(exp): # used only for testing the script
    package_target = "%s-planner" % exp.base_dir
    if not exp.version:
        content = os.listdir(package_target)
        if len(content) != 1:
            err = "version must be specified if more than one planner version is packaged"
            raise Exception, err
        exp.version = content[0]
    package_location = os.path.join(package_target, exp.version)
    if not os.path.exists(package_location):
        raise Exception, "did not find planner version %s" % exp.version
    return package_location

def prepare_planner(exp, compile_m32=False):
    package_path = os.path.abspath(os.path.join(os.curdir, exp.package))
    package_target = "%s-planner" % exp.base_dir

    # extract planner
    package = tarfile.open(package_path)
    os.mkdir(package_target)
    package.extractall(path=package_target)

    # compile planner
    if not exp.version:
        content = os.listdir(package_target)
        if len(content) != 1:
            shutil.rmtree(package_target)
            err = "version must be specified if more than one planner version is packaged"
            raise Exception, err
        exp.version = content[0]
    package_location = os.path.join(package_target, exp.version)
    if not os.path.exists(package_location):
        raise Exception, "did not find planner version %s" % exp.version
    # changing -m64 compiler option to -m32 for Fast Downward
    if compile_m32:
        preprocess_change = 'sed -i -e "s/-m64/-m32/g" %s/src/preprocess/Makefile' % package_location 
        search_change = 'sed -i -e "s/-m64/-m32/g" %s/src/search/Makefile' % package_location 
        print preprocess_change
        print search_change
        print os.path.abspath(os.curdir)
        subprocess.call(preprocess_change, shell=True)
        subprocess.call(search_change, shell=True)
    orig_dir = os.path.abspath(os.curdir)
    os.chdir(package_location) # we properly want to simulate the IPC setting
    try:
        subprocess.call("./build")
    except:
        shutil.rmtree(package_target)
        raise Exception, "error when building planner"
    finally:
        os.chdir(orig_dir)
    return package_location


def build_experiment():
    parser = experiments.ExpArgParser()
    parser.add_argument('-p', '--package', required=True,
                            help="planner package (tar.gz)")
    version_help =  "planner version (e.g. seq-opt-bjolp); "
    version_help += "required if several versions are included in the package"
    parser.add_argument('-v', '--version', default=None,
                            help=version_help)
    parser.add_argument('-s', '--suite', default=[], type=tools.csv,
                            required=True, help=downward_suites.HELP)

    exp = experiments.build_experiment(parser)
    problems = downward_suites.build_suite(exp.suite)
    planner_dir_from = None
    try:
        planner_dir_from = prepare_planner(exp, compile_m32=True)
#        planner_dir_from = reuse_planner(exp)
    except Exception, err:
        raise SystemExit('Error: Could not prepare planner: %s' % err)

    planner_dir = exp.version
    for problem in problems:
        run = exp.add_run()
        run.add_resource(exp.version + '_DIR', planner_dir_from,
                     planner_dir)
        
        # Set memory limit in KB
        run.set_property('memory_limit', exp.memory * 1024)

        domain_file = problem.domain_file()
        problem_file = problem.problem_file()
        run.set_property('domain', problem.domain)
        run.set_property('problem', problem.problem)
        run.add_resource("DOMAIN", domain_file, "%s/domain.pddl" % planner_dir)
        run.add_resource("PROBLEM", problem_file, "%s/problem.pddl" % planner_dir)

        run.set_preprocess('')
        cmd = 'cd %s && ./plan $DOMAIN $PROBLEM sas_plan' % planner_dir
        run.set_command(cmd)

        run.set_property('config', exp.version)
        run.set_property('id', [exp.version, problem.domain, problem.problem])

        postprocess = 'cp %s/*.groups %s/output.sas %s/output %s/sas_plan* .' % tuple(4*[planner_dir])
        run.set_postprocess(postprocess)

    exp.build()
    return exp

if __name__ == '__main__':
    build_experiment()
