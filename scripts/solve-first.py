#! /usr/bin/env python

import repository
import solver

TIMEOUT = 60
MEMORY = 128

for domain in repository.Repository():
    solver.solve(domain.problems[0], TIMEOUT, MEMORY)

