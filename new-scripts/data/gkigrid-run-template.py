#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import resource
import signal
import socket
import sys
import time
import subprocess

***ENVIRONMENT_VARIABLES***

timeout = ***TIMEOUT***
memory = ***MEMORY***       # Memory in MiB
memory *= 1024 * 1024       # Memory in Bytes


KILL_DELAY = 5               # how long we wait between SIGTERM and SIGKILL
CHECK_INTERVAL = 5           # how often we query the process group status


def set_limit(kind, amount):
    try:
        resource.setrlimit(kind, (amount, amount))
    except OSError, e:
        print >> sys.stderr, "error: %s" % e
        
        
redirects = {'stdout': open('run.log', 'w'), 'stderr': open('run.err', 'w')}


preprocess_command = """***PREPROCESS_COMMAND***"""
if preprocess_command:
    retcode = subprocess.call(preprocess_command, shell=True, **redirects)


set_limit(resource.RLIMIT_CPU, timeout)
set_limit(resource.RLIMIT_AS, memory)
set_limit(resource.RLIMIT_CORE, 0)


run = subprocess.Popen("""***RUN_COMMAND***""", shell=True, **redirects)
run.wait()

# Save the returncode in an environment variable
os.environ['RETURNCODE'] = str(run.returncode)


postprocess_command = """***POSTPROCESS_COMMAND***"""
if postprocess_command:
    retcode = subprocess.call(postprocess_command, shell=True, **redirects)
