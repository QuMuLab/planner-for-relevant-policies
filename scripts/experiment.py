#! /usr/bin/env python

from optparse import OptionParser

import actions
import parallel
import suites
import tools

EXPERIMENT = {"timeout": 1800, "memory": 2048, "suite": None, "configurations": None,
              "debug": False}
# defaults; updated with experiment specification and command line parameters

HELP='''Run certain CONFIGURATIONs of the search component on the
specified SUITE. 

A configuration can be any configuration that is specified in
planner_configurations.py. The suite can consist of domains (e.g. "rovers"),
problems (e.g. "gripper:prob05.pddl"), or predefined problem suites
(e.g. "ALL", "TEST"). The tasks of the suite should already have been
preprocessed. Configurations, suite, timeout and memory can also be
defined in an experiment definition file (if certain aspects are defined
in both ways, the command line options override the definitions from the
file.)'''
def parse_options():
    def parse_comma_list(option, opt, value, parser):
      setattr(parser.values, option.dest, value.split(','))

    parser = OptionParser("usage: %prog [options]",
                          description=HELP)
    parallel.populate_option_parser(parser)
    parser.add_option(
        "-e", "--experiment", action="store", dest="exp_filename",
        help="file containing an experiment definition")
    parser.add_option(
        "-c", "--configs", action="callback", type="string", 
        callback=parse_comma_list, dest="configurations",
        help="comma-separated list of configurations")
    parser.add_option(
        "-s", "--suite", action="callback", type="string", 
        callback=parse_comma_list, dest="suite",
        help="comma-separated list of tasks, domains or suites")
    parser.add_option(
        "-t", "--timeout", action="store", type=int, dest="timeout",
        help="timeout per task in seconds (default is 1800)")
    parser.add_option(
        "-m", "--memory", action="store", type=int, dest="memory",
        help="memory limit per task in MB (default is 2048)")
    parser.add_option(
        "-d", "--debug", action="store_true", dest="debug",
        help="quick test mode: run search executable compiled with debug information, " + \
        "translate and preprocess if necessary, always conduct fresh search, " + \
        "print output to screen")
    options, args = parser.parse_args()
    assert len(args) == 0
    return options


def setup_experiment_settings(options):
    if options.exp_filename:
        read_experiment_file(options.exp_filename)
    update_experiment(EXPERIMENT, options.__dict__)
    if not EXPERIMENT["suite"]:
        raise SystemExit("Error: You need to specify a suite")
    if not EXPERIMENT["configurations"]:
        raise SystemExit("Error: You need to specify at least one planner configuration")
    EXPERIMENT["suite_tasks"] = suites.build_suite(EXPERIMENT["suite"])


def update_experiment(exp, update_dict):
    for key in exp:
        if update_dict.get(key) is not None:
            exp[key] = update_dict[key]
    

def read_experiment_file(filename):
    glob = {}
    execfile(filename, glob, EXPERIMENT)

def main():
    options = parse_options()
    setup_experiment_settings(options)

    jobs = [(problem, config)
            for problem in EXPERIMENT["suite_tasks"]
            for config in EXPERIMENT["configurations"]]

    print jobs
        
    def run_problem((problem, config), log_func):
        log_func("Solving %s with %s..." % (problem, config))
        err_msg = actions.do_search(problem, config, EXPERIMENT["timeout"], EXPERIMENT["memory"],
                                    EXPERIMENT["debug"])
        return err_msg
   
    tools.log("Solving %d problems in %d configurations." % (
        len(EXPERIMENT["suite_tasks"]), len(EXPERIMENT["configurations"])))
    parallel.run_jobs(options.jobs, jobs, run_problem)


if __name__ == "__main__":
    main()
