#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import resource
import sys
import time
import subprocess
import glob
import datetime

***ENVIRONMENT_VARIABLES***

timeout = ***TIMEOUT***
memory = ***MEMORY***       # Memory in MiB
memory *= 1024 * 1024       # Memory in Bytes


KILL_DELAY = 5               # how long we wait between SIGTERM and SIGKILL
CHECK_INTERVAL = 0.5           # how often we query the process group status

# make sure we're in the run directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

redirects = {'stdout': open('run.log', 'a'), 'stderr': open('run.err', 'a')}
properties_file = open('properties', 'a')

def set_limit(kind, amount):
    try:
        resource.setrlimit(kind, (amount, amount))
    except (OSError, ValueError), e:
        redirects['stderr'].write('Error: %s\n' % e)
        sys.exit()

def add_property(name, value):
    properties_file.write('%s = %s\n' % (name, repr(value)))
    properties_file.flush()

def save_returncode(command_name, value):
    os.environ['%s_RETURNCODE' % command_name.upper()] = str(value)
    add_property('%s_returncode' % command_name.lower(), str(value))
    # TODO: Do we want to mark errors here already?
    #if value > 0:
    #    add_property('%s_error' % command_name.lower(), str(value))

def run_command(command, name):
    """
    Calls the command with subprocess.call()
    The timeout does not have to be checked here since the subprocess is
    automatically stopped when the timeout is reached. In that case returncode
    gets the value 137 and the rest of the method is still executed.
    """
    start_times = os.times()
    
    add_property(name + '_start_time', str(datetime.datetime.now()))

    try:
        returncode = subprocess.call(command, shell=True, **redirects)
    except MemoryError:
        redirects['stderr'].write('Error: MemoryError\n')
        # TODO: what is a good memory error returncode?
        returncode = 888
    except KeyboardInterrupt:
        redirects['stdout'].write('%s interrupted\n' % name)
        # TODO: what is a good keyboard interrupt returncode?
        returncode = 999
    
    end_times = os.times()
    time = end_times[2] + end_times[3] - start_times[2] - start_times[3]
    add_property(name + '_time', round(time, 3))
    
    save_returncode(name, returncode)
    return returncode


preprocess_command = """***PREPROCESS_COMMAND***"""
run_command(preprocess_command, 'preprocess')

# Limits can not be increased, so set them only once after the preprocessing
set_limit(resource.RLIMIT_CPU, timeout)
set_limit(resource.RLIMIT_AS, memory)
set_limit(resource.RLIMIT_CORE, 0)

command = """***RUN_COMMAND***"""
returncode = run_command(command, 'command')


optional_output = ***OPTIONAL_OUTPUT***
required_output = ***REQUIRED_OUTPUT***
resources = ***RESOURCES***
run_files = ['run', 'run.log', 'run.err', 'properties']

# Check the output files
if returncode == 0:
    found_files = os.listdir('.')

    detected_optional_files = []
    for file_glob in optional_output:
        detected_optional_files.extend(glob.glob(file_glob))

    expected_files = resources + run_files + detected_optional_files + \
                     required_output

    for file in found_files:
        if file not in expected_files:
            # We have more files than expected
            redirects['stderr'].write('Error: Unexpected file "%s"\n' % file)
    for required_file in required_output:
        if not required_file in found_files:
            # We are missing a required file
            msg = 'Error: Required file missing "%s"\n' % required_file
            redirects['stderr'].write(msg)


postprocess_command = """***POSTPROCESS_COMMAND***"""
run_command(postprocess_command, 'postprocess')
