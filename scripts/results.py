#! /usr/bin/env python2.5

from optparse import OptionParser

import reports
import suites


HELP='''Create a report of the experimental results for the specified
INPUTs in a certain MODE. An input can be a domain (e.g. "rovers"), a
problem (e.g. "gripper:prob05.pddl"), or a predefined problem suite
(e.g. "ALL", "TEST"). The inputs should already have been
preprocessed. The various MODEs are defined in reports.py.'''

def parse_options():
    parser = OptionParser("usage: %prog [options] MODE [INPUT ...]",
                          description=HELP)
    options, args = parser.parse_args()
    if not args:
        parser.error("must specify a report MODE")

    options.report = args[0]
    options.suite = suites.build_suite(args[1:])
    return options


def main():
    options = parse_options()
    reports.do_report(options.report, options.suite)


if __name__ == "__main__":
    main()
