#! /bin/bash

CONFIGS=issue28_configs.py:configs
QUEUE=opteron_core.q

## For the real experiment, use this:
SUITE=ALL
EXPTYPE=gkigrid

## For testing, use this:
#SUITE=gripper:prob01.pddl,gripper:prob02.pddl
#EXPTYPE=local

EXPMODULE=issue28.py

source experiment.sh
