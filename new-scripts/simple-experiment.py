#! /usr/bin/env python
"""
Simple script to demonstrate the use of experiments.py
"""
import os

import experiments
import planning_suites

# We can add our own commandline parameters
parser = experiments.ExpArgParser()
parser.add_argument('-s', '--suite', default=[], nargs='+',
                        help='tasks, domains or suites')

# Factory for experiments.
#
# Parses cmd-line options to decide whether this is a gkigrid
# experiment or a local experiment.
# NOTE: All parameters are given to the experiment instance
exp = experiments.build_experiment(parser=parser)

# Includes a "global" file, i.e., one needed for all runs, into the
# experiment archive. In case of GkiGridExperiment, copies it to the
# main directory of the experiment. The name "PLANNER" is an ID for
# this resource that can also be used to refer to it in shell scripts.
exp.add_resource("PLANNER", "../downward/search/downward",
                        "downward")

problems = planning_suites.build_suite(exp.suite)

for problem in problems:
    # Adds a new run to the experiment and returns it
    run = exp.add_run()
    
    # Make the planner resource available for this run.
    # In environments like the argo cluster, this implies
    # copying the planner into each task. For the gkigrid, we merely
    # need to set up the PLANNER environment variable.
    run.require_resource('PLANNER')
    
    domain_file = problem.domain_file()
    problem_file = problem.problem_file()
    
    # Copy "../benchmarks/domain/domain.pddl" into the run
    # directory under name "domain.pddl" and make it available as
    # resource "DOMAIN" (usable as environment variable $DOMAIN).
    run.add_resource('DOMAIN', domain_file, 'domain.pddl')
    run.add_resource('PROBLEM', problem_file, 'problem.pddl')
    
    translator_path = '../downward/translate/translate.py'
    translator_path = os.path.abspath(translator_path)
    translate_cmd = '%s %s %s' % (translator_path, domain_file, problem_file)
    
    preprocessor_path = '../downward/preprocess/preprocess'
    preprocessor_path = os.path.abspath(preprocessor_path)
    preprocess_cmd = '%s < %s' % (preprocessor_path, 'output.sas')
    
    # Optionally, can use run.set_preprocess() and
    # run.set_postprocess() to specify code that should be run
    # before the main command, i.e., outside the part for which we
    # restrict runtime and memory. For example, post-processing
    # could be used to rename result files or zipping them up. The
    # postprocessing code can find out whether the command succeeded 
    # or was aborted via the environment variable $RETURNCODE
    run.set_preprocess('%s; %s' % (translate_cmd, preprocess_cmd))
    
    # A bash fragment that gives the code to be run when invoking
    # this job.
    run.set_command("$PLANNER --search 'astar(cea())' < output")
    
    # Specifies that all files names "plan.soln*" (using
    # shell-style glob patterns) are part of the experiment output.
    # There's a corresponding declare_required_output for output
    # files that must be present at the end or we have an error. A
    # specification like this is e.g. necessary for the Argo
    # cluster. On the gkigrid, this wouldn't do anything, although
    # the declared outputs are stored so that we
    # can later verify that all went according to plan.
    run.declare_optional_output('*.groups')
    run.declare_optional_output('output')
    run.declare_optional_output('output.sas')
    run.declare_optional_output('sas_plan')
    
    # Set some properties to be able to analyze the run correctly
    # The properties are written into the "properties" file
    run.set_property('config', 'astar-cea')
    run.set_property('domain', problem.domain)
    run.set_property('problem', problem.problem)
    # The run's id determines the directory it will be copied to by resultfetcher
    run.set_property('id', ['astar-cea', problem.domain, problem.problem])

# Actually write and copy all the files
exp.build()

