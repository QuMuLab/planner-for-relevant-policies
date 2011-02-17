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
from log import redirects, save_returncode


"""VARIABLES"""

"""CALLS"""
