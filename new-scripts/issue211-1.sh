#! /bin/bash

CONFIGS=issue211_configs.py:configs
QUEUE=opteron_core.q

## For testing, use this:
#SUITE=gripper:prob01.pddl,gripper:prob02.pddl
#EXPTYPE=local

## For the real experiment, use this:
SUITE=OPTIMAL
EXPTYPE=gkigrid

# export MAGIC_OVERRIDE_REVISION=ff196fd6615f

source experiment.sh
