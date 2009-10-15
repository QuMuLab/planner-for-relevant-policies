#! /usr/bin/env python

from optparse import OptionParser

import actions
import suites
import tools


TIMEOUT = 1800
MEMORY = 2048 - 256

CONFIGURATIONS = [
    "c",  # causal graph heuristic
    "d",  # additive heuristic
    "f",  # FF heuristic
    "y",  # context-enhanced additive heuristic
    "cd", "cf", "cy", "df", "dy", "fy",
    "cdf", "cdy", "cfy", "dfy",
    "cdfy",
    ]

HELP='''Generate a directory DIR containing the experimental setup for
running certain configurations of the search component on the Black
Forest Grid, on the specified INPUTs. An input can be a domain (e.g.
"rovers"), a problem (e.g. "gripper:prob05.pddl"), or a predefined
problem suite (e.g. "ALL", "TEST"). The inputs should already have
been preprocessed.'''
def parse_options():
    parser = OptionParser("usage: %prog [options] DIR [INPUT ...]",
                          description=HELP)
    options, args = parser.parse_args()
    if not args:
        parser.error("need a name for the work directory")
    options.workdir = args[0]
    options.suite = suites.build_suite(args[1:])
    options.configurations = CONFIGURATIONS
    # TODO: MEMORY, TIMEOUT and CONFIGURATIONS should be configurable
    #       on the command line.
    options.memory = MEMORY
    options.timeout = TIMEOUT
    return options


def main():
    options = parse_options()
    tools.log("Preparing workdir...")
    actions.prepare_workdir(options.workdir)
    for problem in options.suite:
        tools.log("Preparing problem %s..." % problem)
        actions.prepare_problem(options.workdir, problem)
        for config in options.configurations:
            tools.log("Preparing job %s [%s]..." % (problem, config))
            actions.prepare_job_search(
                options.workdir, problem, config,
                options.timeout, options.memory)


if __name__ == "__main__":
    main()
