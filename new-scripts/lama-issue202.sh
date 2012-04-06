#! /bin/bash

CONFIGS=downward_configs.py:lama
QUEUE=athlon_core.q

## For testing, use this:
#SUITE=gripper:prob01.pddl,gripper:prob02.pddl
#EXPTYPE=local

## For the real experiment, use this:
SUITE=IPC08_SAT_STRIPS,STRIPS_IPC12345
EXPTYPE=gkigrid

source experiment.sh
