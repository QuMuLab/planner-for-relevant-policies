#! /usr/bin/env python

import sys
import os
import multiprocessing
import subprocess
import time

# make sure we're in the run directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))


def run_cmd(command):
    try:
        run = subprocess.call(command, shell=True, stdout=sys.stdout, stderr=sys.stderr)
    except KeyboardInterrupt:
        print 'Call to run interrupted'
        run.terminate()

commands = [\
***COMMANDS***
]

pool = multiprocessing.Pool(processes=***PROCESSES***)
res = pool.map_async(run_cmd, commands)
pool.close()

try:
    pool.join()
except KeyboardInterrupt:
    print 'Main script interrupted'
    pool.terminate()
