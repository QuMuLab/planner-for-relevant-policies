#! /bin/bash

CONFIGS=ipc11
QUEUE=opteron_core.q

## For the real experiment, use this:
SUITE=IPC08_SAT_STRIPS
EXPTYPE=gkigrid

## For testing, use this:
#SUITE=gripper:prob01.pddl,gripper:prob02.pddl
#EXPTYPE=local

EXPMODULE=issue102.py

source experiment.sh
