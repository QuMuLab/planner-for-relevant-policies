#! /bin/bash

CONFIGS=downward_configs.py:alternation_configs
QUEUE=athlon_core.q

## For testing, use this:
#SUITE=gripper:prob01.pddl,gripper:prob02.pddl
#EXPTYPE=local

## For the real experiment, use this:
SUITE=IPC08_SAT_STRIPS
EXPTYPE=gkigrid

source experiment.sh
