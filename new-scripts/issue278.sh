#! /bin/bash

CONFIGS=lama
QUEUE=opteron_core.q

## For the real experiment, use this:
SUITE=ALL
EXPTYPE=gkigrid

## For testing, use this:
#SUITE=gripper:prob01.pddl,gripper:prob02.pddl
#EXPTYPE=local

EXPMODULE=issue278.py

source experiment.sh
