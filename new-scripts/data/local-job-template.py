#! /usr/bin/env python

import sys
import multiprocessing
import subprocess
import time

def run_cmd(command):
    try:
        run = subprocess.call(command, shell=True)
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
