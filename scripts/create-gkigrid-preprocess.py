#! /usr/bin/env python

from optparse import OptionParser

import actions
import suites

TIMEOUT = 3600

HELP='''Generate a job file JOBFILE to run the translator and
preprocessor on the GKI grid. An input can be a domain (e.g.
"rovers"), a problem (e.g. "gripper:prob05.pddl"), or a predefined
problem suite (e.g. "ALL", "TEST").'''

def parse_options():
    parser = OptionParser("usage: %prog JOBFILE [INPUT ...]",
                          description=HELP)
    options, args = parser.parse_args()
    if not args:
        parser.error("need a name for the job file")
    options.jobfile = args[0]
    options.suite = suites.build_suite(args[1:])
    return options


def main():
    options = parse_options()
    actions.prepare_gkigrid_job_preprocess(
        options.jobfile, options.suite, timeout=TIMEOUT)
            

if __name__ == "__main__":
    main()
