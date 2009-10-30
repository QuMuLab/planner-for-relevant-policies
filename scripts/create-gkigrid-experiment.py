#! /usr/bin/env python

from optparse import OptionParser

import actions
import suites
import tools


TIMEOUT = 1800
MEMORY = 2048

CONFIGURATIONS = [
    "oaX", # A* with merge-and-shrink; domain-dependent parameters
           # will be added in place of X.
    ]

HELP='''Generate a job file JOBFILE to run certain configurations of
the search component on the GKI grid.
An input can be a domain (e.g. "rovers"), a problem (e.g.
"gripper:prob05.pddl"), or a predefined problem suite (e.g. "ALL",
"TEST"). The inputs should already have been preprocessed.'''
def parse_options():
    parser = OptionParser("usage: %prog [options] JOBFILE [INPUT ...]",
                          description=HELP)
    options, args = parser.parse_args()
    if not args:
        parser.error("need a name for the job file")
    options.jobfile = args[0]
    options.suite = suites.build_suite(args[1:])
    options.configurations = CONFIGURATIONS
    # TODO: MEMORY, TIMEOUT and CONFIGURATIONS should be configurable
    #       on the command line.
    options.memory = MEMORY
    options.timeout = TIMEOUT
    return options


def main():
    options = parse_options()
    actions.prepare_gkigrid_job_search(
        options.jobfile, options.suite, options.configurations,
        options.timeout, options.memory)
            

if __name__ == "__main__":
    main()
