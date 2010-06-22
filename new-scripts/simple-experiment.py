import experiments

parser = experiments.ExpOptionParser()
parser.add_option(
    "-c", "--configs", action="extend", type="string",
    dest="configurations", default=[],
    help="comma-separated list of configurations")
parser.add_option(
    "-s", "--suite", action="extend", type="string", 
    dest="suite", default=[],
    help="comma-separated list of tasks, domains or suites")

experiment = experiments.build_experiment(parser=parser)
## Factory for experiments.
##
## Parses cmd-line options to decide whether this is a gkigrid
## experiment, a local experiment or whatever, and what the name
## of the experiment (the *.q file etc.) should be.
##
## Also parses options to override the default values for sharding
## (how many tasks to group into one top-level directory) and
## grouping (how many runs to put into one task).
##
## Maybe also parses some generic options that make sense for all
## kinds of experiments, e.g. timeout and memory limit.

experiment.add_resource("PLANNER", "../downward/search/release-search",
                        "release-search")
## Includes a "global" file, i.e., one needed for all runs, into the
## experiment archive. In case of GkiGridExperiment, copies it to the
## main directory of the experiment. The name "PLANNER" is an ID for
## this resource that can also be used to refer to it in shell scripts.

for prob_no in xrange(1, 20 + 1):
    configs = experiment.configurations
    if not configs:
        experiment.parser.error('You need to specify at least one configuration')
    for options in ["ou", "fF"]:
        prob_path = "gripper/prob%02d.pddl" % prob_no
        #run = experiments.Run()
        run = experiment.add_run()
        run.require_resource("PLANNER")
        # Make the planner resource available for this task.variable
        # In environments like the argo cluster, this implies
        # copying the planner into each task. For the gkigrid, we merely
        # need to set up the PLANNER environment variable.
        run.add_resource(
            "DOMAIN", "../benchmarks/gripper/domain.pddl",
            "domain.pddl")
        # Copy "../benchmarks/gripper/domain.pddl" into the run
        # directory under name "domain.pddl" and make it available as
        # resource "DOMAIN" (usable as environment variable $DOMAIN).
        run.add_resource(
            "PROBLEM", "../benchmarks/%s" % prob_path, "problem.pddl")
        run.add_resource(
            "INFILE", "../results/preprocess/%s/output" % prob_path,
            "output")
        run.set_command("$PLANNER %s < $INFILE" % options)
        ## A bash fragment that gives the code to be run when invoking
        ## this job.
        run.set_preprocess('ls -l')
        run.set_postprocess('echo the command returned $RETURNCODE')
        ## Optionally, can use run.set_preprocess() and
        ## run.set_postprocess() to specify code that should be run
        ## before the main command, i.e., outside the part for which we
        ## restrict runtime and memory. For example, post-processing
        ## could be used to rename result files or zipping them up. The
        ## postprocessing code should have some way of finding out
        ## whether the command succeeded or was aborted, e.g. via some
        ## environment variable.
        run.declare_optional_output("plan.soln*")
        ## Specifies that all files names "plan.soln*" (using
        ## shell-style glob patterns) are part of the experiment output.
        ## There's a corresponding declare_required_output for output
        ## files that must be present at the end or we have an error. A
        ## specification like this is e.g. necessary for the Argo
        ## cluster. On the gkigrid, this wouldn't do anything, although
        ## the declared outputs should be stored somewhere so that we
        ## can later verify that all went according to plan.
        #experiment.add_run(run)
        ## Schedule this run to be part of the experiment.





experiment.build()

