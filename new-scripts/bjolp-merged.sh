#! /bin/bash

CONFIGS=downward_configs.py:lmopt_rhw,downward_configs.py:lmopt_rhw_hm1
QUEUE=athlon_core.q

## For testing, use this:
#SUITE=gripper:prob01.pddl,gripper:prob02.pddl
#EXPTYPE=local

## For the real experiment, use this:
SUITE=OPTIMAL
EXPTYPE=gkigrid

source experiment.sh
