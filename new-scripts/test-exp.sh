#! /bin/bash

EXPNAME=exp-test

CONFIGS=yY,downward_configs.py:multiple_plans,iterated_search,../src/search/downward-seq-sat-fdss-1.py,../src/search/downward-seq-opt-fdss-1.py
QUEUE=xeon_core.q

SUITE=gripper:prob01.pddl,gripper:prob02.pddl,zenotravel:pfile1

if [[ "$(hostname)" != habakuk ]]; then
    EXPTYPE=local
else
    EXPTYPE=gkigrid
fi

# Can be used for testing --complete or --compact experiments
EXPOPTS=

# We only want a quick look if everything worked
REPORTATTRS='-a coverage';

source experiment.sh
