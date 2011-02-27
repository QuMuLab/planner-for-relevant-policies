#! /bin/bash

EXPNAME=test-exp

CONFIGS=downward_configs.py:yY
QUEUE=athlon_core.q

SUITE=MINITEST
EXPTYPE=local

# We only want a quick look if everything worked
REPORTATTRS='-a coverage';

source experiment.sh
