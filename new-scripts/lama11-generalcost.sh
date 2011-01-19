#! /bin/bash

CONFIGS=downward_configs.py:lama11_generalcost
QUEUE=athlon.q

## For testing, use this:
#SUITE=blocks:probBLOCKS-6-0.pddl,elevators-sat08-strips:p01.pddl
#EXPTYPE=local

## For the real experiment, use this:
SUITE=IPC08_SAT_STRIPS
EXPTYPE=gkigrid

source experiment.sh
