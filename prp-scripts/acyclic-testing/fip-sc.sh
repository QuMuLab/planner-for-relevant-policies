#! /bin/bash

python /u/cjmuise/EXPERIMENTS/strong-prp/prp-scripts/determinizer.py FIP $1 fip-domain.pddl
/u/cjmuise/EXPERIMENTS/fip/fip -o fip-domain.pddl -f $2
