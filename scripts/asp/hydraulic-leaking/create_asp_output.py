#! /usr/bin/env python

import sys

def output_plan():
    timestep = 0
    for line in open(sys.argv[2]):
        line.strip()
        assert line.startswith("(")
        line = line[1:]
        predicate = line.split("-")[0]
        valve = line.split()[1]
        print predicate + "(" + valve[1:] + "," + str(timestep) + ").",
        timestep += 1
    print

# Read search log passed in as arg
for line in open(sys.argv[1]):
    if line.strip() == "Completely explored state space -- no solution!":
        print "INCONSISTENT"
        break
    elif line.strip() == "Solution found!":
        output_plan()
        print "ANSWER SET FOUND"
        break
