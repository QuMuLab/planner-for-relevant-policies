#! /bin/bash

CONFIGS=downward_configs.py:lama11_unitcost
QUEUE=opteron_core.q

## For testing, use this:
#SUITE=blocks:probBLOCKS-7-0.pddl,elevators-sat08-strips:p01.pddl
#EXPTYPE=local

## For the real experiment, use this:
SUITE=STRIPS_IPC12345
EXPTYPE=gkigrid

source experiment.sh
