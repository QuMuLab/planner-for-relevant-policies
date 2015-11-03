#! /bin/bash

python /home/cjmuise/Projects/strong-prp/prp-scripts/strong-acyclic-conversion.py $1 strong-domain.pddl 1
/home/cjmuise/Projects/strong-prp/src/prp strong-domain.pddl $2
