#! /bin/bash

#python /home/cjmuise/Projects/strong-prp/prp-scripts/strong-acyclic-conversion.py $1 strong-domain.pddl 1
#/home/cjmuise/Projects/grendel/grendel_astar.py strong-domain.pddl $2
python /u/cjmuise/EXPERIMENTS/strong-prp/prp-scripts/strong-acyclic-conversion.py $1 strong-domain.pddl 1
/u/cjmuise/EXPERIMENTS/grendel/grendel_astar.py strong-domain.pddl $2
