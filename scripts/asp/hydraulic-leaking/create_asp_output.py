#! /usr/bin/env python

import sys
timestep = 0
for line in open(sys.argv[1]):
    line.strip()
    assert line.startswith("(")
    line = line[1:]
    predicate = line.split("-")[0]
    valve = line.split()[1]
    print predicate + "(" + valve[1:] + "," + str(timestep) + ").",
    timestep += 1
