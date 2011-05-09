#! /bin/bash

EXPNAME=test-exp

CONFIGS=downward_configs.py:yY
QUEUE=athlon_core.q

SUITE=gripper:prob01.pddl,zenotravel:pfile1

if [[ "$(hostname)" != habakuk ]]; then
    EXPTYPE=local
else
    EXPTYPE=gkigrid
fi


# We only want a quick look if everything worked
REPORTATTRS='-a coverage';

source experiment.sh
