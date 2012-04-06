#! /bin/bash

CONFIGS=mas_configs.py:configs_jacm_hhh_with_label_reduction
QUEUE=opteron_core.q

## For the real experiment, use this:
SUITE=OPTIMAL_WITH_IPC11
EXPTYPE=gkigrid

## For testing, use this:
#SUITE=gripper:prob01.pddl,gripper:prob02.pddl
#EXPTYPE=local

EXPOPTS=--compact
export DOWNWARD_TIMEOUT=1800

source experiment.sh
