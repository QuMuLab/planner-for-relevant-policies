#! /usr/bin/env python
"""
Simple script to demonstrate the use of experiments.py for 
fast downward experiments

Example usage:
./downward-experiments.py test-exp -c downward-configs.py:cfg1 \
                downward-configs.py:cfg3 -s gripper:prob01.pddl
"""
import os
import sys
import logging
from collections import defaultdict

import experiments
import downward_suites


def get_configs(configs_strings):
    """
    Parses configs_strings and returns a list of tuples of the form 
    (configuration_name, configuration_string)
    
    config_strings can contain strings of the form 
    "configs.txt:cfg13" or "configs.txt"
    """
    def parse_configs(file):
        assert file.endswith('.py')
        module_name = file[:-3]
        try:
            module = __import__(module_name)
        except ImportError, err:
            logging.error('File "%s" could not be imported' % file)
            sys.exit(1)
        config_names = [c for c in dir(module) if not c.startswith('_')]
        configs = [(name, getattr(module, name)) for name in config_names]
        return configs
        
    complete_files = []
    files_to_configs = defaultdict(list)
    for config_string in configs_strings:
        if ':' in config_string:
            config_file, config_name = config_string.split(':')
            files_to_configs[config_file].append(config_name)
        else:
            # We have a complete file
            complete_files.append(config_string)
    
    all_configs = []
    
    for file in complete_files:
        all_configs.extend(parse_configs(file))
    
    for file, config_names in files_to_configs.iteritems():
        if file in complete_files:
            # We have already imported this file
            continue
        filtered_configs = [(name, c) for (name, c) in parse_configs(file) \
                            if name in config_names]
        found = [c for (name, c) in filtered_configs]
        not_found = [c for c in config_names if c not in found]
        if not_found:
            logging.error('The configs %s were not found in "%s"' % (not_found, file))
            sys.exit(1)
        all_configs.extend(filtered_configs)
    
    logging.info('Found configs: %s' % all_configs)
    return all_configs
                
    
    

# We can add our own commandline parameters
parser = experiments.ExpArgParser()
parser.add_argument('-s', '--suite', default=[], nargs='+', required=True,
                        help='tasks, domains or suites')
parser.add_argument('-c', '--configs', default=[], nargs='+', required=True,
                        help='e.g. "configs.txt:cfg13" or "configs.txt"')

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
exp.add_resource("PLANNER", "../downward/search/downward", "downward")

problems = downward_suites.build_suite(exp.suite)

for problem in problems:
    for config_name, config_string in get_configs(exp.configs):
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
        run.set_command("$PLANNER %s < output" % config_string)
        
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
        run.set_property('config', config_name)
        run.set_property('domain', problem.domain)
        run.set_property('problem', problem.problem)
        # The run's id determines the directory it will be copied to by resultfetcher
        run.set_property('id', [config_name, problem.domain, problem.problem])

# Actually write and copy all the files
exp.build()

