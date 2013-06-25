#! /usr/bin/env python

import os
import platform
from subprocess import call

from downward.experiment import DownwardExperiment
from downward.reports.absolute import AbsoluteReport
from downward import suites
from lab.steps import Step
from lab.environments import MaiaEnvironment
from lab.environments import LocalEnvironment

# Genereal settings - not needed to be changed usually
NODE = platform.node()
REMOTE = NODE.startswith('gkigrid') or NODE.endswith('cluster') or NODE in ['habakuk', 'turtur']
SCP_LOGIN = 'sieverss@maia'
ATTRIBUTES = ['coverage', 'cost', 'total_time']

REMOTE_EXPS = '/infai/sieverss/experiments'
LOCAL_EXPS = '/home/silvan/experiments'

REMOTE_REPOS = '/infai/sieverss/repos'
LOCAL_REPOS = '/home/silvan/repos/fast-downward'

#REMOTE_PYTHON = '/infai/sieverss/bin/python'
#LOCAL_PYTHON = 'python2.7'

# Settings for current experiment
EXPNAME = 'issue123'
REPO_NAME = '/issue123'
LOCAL_SUITE = ['gripper:prob01.pddl', 'zenotravel:pfile1']
GRID_SUITE = suites.suite_satisficing_with_ipc11()
CONFIGS = {
	#'synergy': ['--heuristic', 'hlm,hff=lm_ff_syn(lm_rhw(reasonable_orders=true))', '--search', 'iterated(lazy_wastar([hlm,hff],w=1,preferred=[hlm,hff]),repeat_last=true)'],
	'separated': ['--heuristic', 'hlm=lmcount(lm_rhw(reasonable_orders=true),pref=true)', '--heuristic', 'hff=ff()', '--search', 'iterated(lazy_wastar([hlm,hff],w=1,preferred=[hlm,hff]),repeat_last=true)']
	}

if REMOTE:
    EXPS = REMOTE_EXPS
    REPOS = REMOTE_REPOS
    ENVIRONMENT = MaiaEnvironment()
    SUITE = GRID_SUITE
#    PYTHON = REMOTE_PYTHON
else:
    EXPS = LOCAL_EXPS
    REPOS = LOCAL_REPOS
    ENVIRONMENT = LocalEnvironment()
    SUITE = LOCAL_SUITE
#    PYTHON = LOCAL_PYTHON

EXPPATH = os.path.join(EXPS, EXPNAME)
REPO = REPOS+REPO_NAME

exp = DownwardExperiment(path=EXPPATH, repo=REPO, environment=ENVIRONMENT)

exp.add_suite(SUITE)
for nick, config in CONFIGS.iteritems():
	exp.add_config(nick, config)

# Make a report containing absolute numbers (this is the normal report).
exp.add_step(Step('report-abs',
                  AbsoluteReport(),
                  exp.eval_dir,
                  os.path.join(exp.eval_dir, '%s-abs.html' % EXPNAME)))

# Publish html report
exp.add_step(Step('publish', call, ['publish', os.path.join(exp.eval_dir, '%s-abs.html' % EXPNAME)]))

# Compress the experiment directory.
exp.add_step(Step.zip_exp_dir(exp))

# Remove the experiment directory.
exp.add_step(Step.remove_exp_dir(exp))

# This method parses the commandline. Invoke the script to see all steps.
exp()
