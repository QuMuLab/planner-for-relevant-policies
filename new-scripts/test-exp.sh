#! /bin/bash

EXPNAME=test-exp

CONFIGS=downward_configs.py:yY,downward_configs.py:multiple_plans
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
