#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# make sure we're in the run directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#TODO: Change
#exp_code_dir = os.path.abspath("../../exp_code")
exp_code_dir = "/home/jendrik/projects/Downward/downward/new-scripts/data"
print exp_code_dir
sys.path.insert(0, exp_code_dir)

from call import Call


***ENVIRONMENT_VARIABLES***

redirects = {'stdout': open('run.log', 'w'), 'stderr': open('run.err', 'w')}
properties_file = open('properties', 'w')


def add_property(name, value):
    properties_file.write('%s = %s\n' % (name, repr(value)))
    properties_file.flush()

def save_returncode(command_name, value):
    add_property('%s_returncode' % command_name.lower(), value)
    # TODO: Do we want to mark errors here already?
    # TODO: Would it be better to save just one "fatal_error" for each run?
    error = 0 if value == 0 else 1
    add_property('%s_error' % command_name.lower(), error)
