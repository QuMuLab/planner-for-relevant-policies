#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import resource
import signal
import socket
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


def set_limit(kind, amount):
    try:
        resource.setrlimit(kind, (amount, amount))
    except OSError, e:
        print >> sys.stderr, "error: %s" % e
        
        
def add_property(name, value):
    file = redirects['stdout']
    file.write('%s : %s\n' % (name, value))
    file.flush()


preprocess_command = """***PREPROCESS_COMMAND***"""
if preprocess_command:
    retcode = subprocess.call(preprocess_command, shell=True, **redirects)


set_limit(resource.RLIMIT_CPU, timeout)
set_limit(resource.RLIMIT_AS, memory)
set_limit(resource.RLIMIT_CORE, 0)

start_time = time.clock()
term_attempted = False

add_property('run_start_time', datetime.datetime.now())

run = subprocess.Popen("""***RUN_COMMAND***""", shell=True, **redirects)

try:
    while True:
        time.sleep(CHECK_INTERVAL)
        
        alive = run.poll() is None
        if not alive:
            break
            
        passed_time = time.clock() - start_time
        if passed_time > timeout and not term_attempted:
            run.terminate()
            term_attempted = True
        elif passed_time > timeout + KILL_DELAY and term_attempted:
            run.kill()
            break
except KeyboardInterrupt:
    print 'Run interrupted'
    run.returncode = 'Interrupted'
    run.terminate()

# Save the returncode in an environment variable
os.environ['RETURNCODE'] = str(run.returncode)


optional_output = ***OPTIONAL_OUTPUT***
required_output = ***REQUIRED_OUTPUT***
resources = ***RESOURCES***
run_files = ['run', 'run.log', 'run.err', 'properties']

# Check the output files
if run.returncode == 0:
    found_files = os.listdir('.')
    
    detected_optional_files = []
    for file_glob in optional_output:
        detected_optional_files.extend(glob.glob(file_glob))
        
    expected_files = resources + run_files + detected_optional_files + required_output
    
    for file in found_files:
        if file not in expected_files:
            # We have more files than expected
            redirects['stderr'].write('ERROR: Unexpected file "%s"\n' % file)
    for required_file in required_output:
        if not required_file in found_files:
            # We are missing a required file
            redirects['stderr'].write('ERROR: Required file missing "%s"\n' % required_file)
    


postprocess_command = """***POSTPROCESS_COMMAND***"""
if postprocess_command:
    retcode = subprocess.call(postprocess_command, shell=True, **redirects)
