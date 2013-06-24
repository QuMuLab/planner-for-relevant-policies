#! /usr/bin/env python

import os

from downward.experiment import DownwardExperiment
from downward.reports.absolute import AbsoluteReport
from downward import suites
from lab.steps import Step
from lab.environments import MaiaEnvironment
from lab.environments import LocalEnvironment

# Local and grid definitions
LOCAL_HOME = '/home/silvan'
LOCAL_PATH = LOCAL_HOME+'/aktuell/fast-downward/repos'
GRID_HOME = '/infai/sieverss'
GRID_PATH = GRID_HOME+'/repos'
LOCAL_ENVIRONMENT = LocalEnvironment()
GRID_ENVIRONMENT = MaiaEnvironment()
LOCAL_SUITE = ['gripper:prob01.pddl', 'zenotravel:pfile1']
GRID_SUITE = suites.suite_satisficing_with_ipc11()

# Switch between local or grid experiment setup
LOCAL = 0
if (LOCAL == 1):
	HOME = LOCAL_HOME
	PATH = LOCAL_PATH
	ENVIRONMENT = LOCAL_ENVIRONMENT
	SUITE = LOCAL_SUITE
else:
	HOME = GRID_HOME
	PATH = GRID_PATH
	ENVIRONMENT = GRID_ENVIRONMENT
	SUITE = GRID_SUITE

EXPNAME = 'issue123'
EXPPATH = os.path.join(HOME+'/experiments', EXPNAME)
REPO = PATH+'/fd-issue123'

exp = DownwardExperiment(path=EXPPATH, repo=REPO, environment=ENVIRONMENT)

exp.add_suite(SUITE)
exp.add_config('synergy', ['--heuristic', 'hlm,hff=lm_ff_syn(lm_rhw(reasonable_orders=true))', '--search', 'iterated(lazy_wastar([hlm,hff],w=1,preferred=[hlm,hff]),repeat_last=true)'])
exp.add_config('separated', ['--heuristic', 'hlm=lmcount(lm_rhw(reasonable_orders=true),pref=true)', '--heuristic', 'hff=ff()', '--search', 'iterated(lazy_wastar([hlm,hff],w=1,preferred=[hlm,hff]),repeat_last=true)'])

# Make a report containing absolute numbers (this is the normal report).
exp.add_step(Step('report-abs',
                  AbsoluteReport(),
                  exp.eval_dir,
                  os.path.join(exp.eval_dir, '%s-abs.html' % EXPNAME)))

# Compress the experiment directory.
exp.add_step(Step.zip_exp_dir(exp))

# Remove the experiment directory.
exp.add_step(Step.remove_exp_dir(exp))

# This method parses the commandline. Invoke the script to see all steps.
exp()
