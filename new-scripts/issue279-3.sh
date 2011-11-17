#! /bin/bash

CONFIGS=issue279_configs.py:configs_goal_cg_level
QUEUE=opteron_core.q

## For the real experiment, use this:
SUITE=OPTIMAL
EXPTYPE=gkigrid

## For testing, use this:
#SUITE=gripper:prob01.pddl,gripper:prob02.pddl
#EXPTYPE=local

source experiment.sh
