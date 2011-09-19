#! /bin/bash

CONFIGS=downward_configs.py:raz_ipc
QUEUE=opteron_core.q

## For testing, use this:
#SUITE=gripper:prob01.pddl,gripper:prob02.pddl
#EXPTYPE=local

## For the real experiment, use this:
SUITE=STRIPS_IPC12345,IPC08_OPT_STRIPS
EXPTYPE=gkigrid

source experiment.sh
