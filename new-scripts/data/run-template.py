#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# make sure we're in the run directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

exp_code_dir = os.path.abspath("../../calls")
sys.path.insert(0, exp_code_dir)

from call import Call
from log import print_, redirects, save_returncode, driver_log, driver_err

sys.stdout = driver_log
sys.stderr = driver_err


"""VARIABLES"""

"""CALLS"""
