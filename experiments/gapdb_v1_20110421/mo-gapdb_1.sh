#! /bin/bash

CONFIGS=downward_configs.py:gapdb_e10,gapdb_e20,gapdb_e30,gapdb_e40,gapdb_e50,gapdb_e60,gapdb_e70,gapdb_e80,gapdb_e90,gapdb_e100
QUEUE=opteron_core.q

## For testing, use this:
#SUITE=blocks:probBLOCKS-4-2.pddl,blocks:probBLOCKS-7-2.pddl
#EXPTYPE=local

## For the real experiment, use this:
SUITE=PDB_TESTS
EXPTYPE=gkigrid

source experiment.sh
