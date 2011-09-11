#! /bin/bash

CONFIGS=mas_configs.py:configs_mas_all
QUEUE=opteron_core.q

## For the real experiment, use this:
SUITE=ALL
EXPTYPE=gkigrid

## For testing, use this:
#SUITE=gripper:prob01.pddl,gripper:prob02.pddl
#EXPTYPE=local

EXPMODULE=issue276.py

source experiment.sh
