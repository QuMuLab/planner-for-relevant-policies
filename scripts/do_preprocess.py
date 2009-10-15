#! /usr/bin/env python

from optparse import OptionParser

import actions
import parallel
import suites


HELP='''Run translator and preprocessor on the specified INPUTs.
An input can be a domain (e.g. "rovers"), a problem
(e.g. "gripper:prob05.pddl"), or a predefined problem suite
(e.g. "ALL", "TEST").'''
def parse_options():
    parser = OptionParser("usage: %prog [options] [INPUT ...]",
                          description=HELP)
    parallel.populate_option_parser(parser)
    parser.add_option(
        "--relax", help="generate relaxed problem",
        action="store_true", default=False, dest="relax")
    options, args = parser.parse_args()
    options.suite = suites.build_suite(args)
    return options

    
if __name__ == "__main__":
    options = parse_options()

    def run_problem(problem, log_func):
        log_func("Translating %s..." % problem)
        success = actions.do_translate(
            problem, generate_relaxed_problem=options.relax)
        if not success:
            return "Translating %s failed, skipping preprocess." % problem
            
        log_func("Preprocessing %s..." % problem)
        success = actions.do_preprocess(problem)
        if not success:
            return "Preprocessing %s failed." % problem
        return None

    parallel.run_jobs(options.jobs, options.suite, run_problem)
