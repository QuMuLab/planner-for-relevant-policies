#! /bin/bash

CONFIGS=mas_configs.py:config_plain_bisimulation
# CONFIGS=mas_configs.py:configs_selectivity_of_bisim
QUEUE=opteron_core.q

## For the real experiment, use this:
SUITE=OPTIMAL
EXPTYPE=gkigrid

## For testing, use this:
#SUITE=gripper:prob01.pddl,gripper:prob02.pddl
#EXPTYPE=local

source experiment.sh
