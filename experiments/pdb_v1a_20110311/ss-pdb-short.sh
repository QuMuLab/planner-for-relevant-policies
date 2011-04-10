#! /bin/bash

CONFIGS=downward_configs.py:pdb1000,pdb2500,pdb5000,pdb10000,pdb25000,pdb50000,pdb100000,pdb250000,pdb500000,pdb1000000,pdb2500000,pdb5000000,pdb10000000,pdb25000000,pdb50000000,pdb100000000
QUEUE=opteron_core.q

## For testing, use this:
#SUITE=blocks:probBLOCKS-4-2.pddl,blocks:probBLOCKS-7-2.pddl
#EXPTYPE=local

## For the real experiment, use this:
SUITE=PDB_TESTS
EXPTYPE=gkigrid

source experiment.sh
