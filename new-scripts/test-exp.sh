#! /bin/bash

EXPNAME=exp-test

CONFIGS=yY,downward_configs.py:multiple_plans,iterated_search
QUEUE=xeon_core.q

SUITE=gripper:prob01.pddl,zenotravel:pfile1

if [[ "$(hostname)" != habakuk ]]; then
    EXPTYPE=local
else
    EXPTYPE=gkigrid
fi


# We only want a quick look if everything worked
REPORTATTRS='-a coverage';

source experiment.sh
