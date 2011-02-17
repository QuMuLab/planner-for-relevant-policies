#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# make sure we're in the run directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

exp_code_dir = os.path.abspath("../../calls")
sys.path.insert(0, exp_code_dir)

from call import Call
from log import redirects, save_returncode


"""VARIABLES"""

"""CALLS"""
