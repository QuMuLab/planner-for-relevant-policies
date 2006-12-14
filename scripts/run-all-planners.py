#! /usr/bin/env python

import os.path as path
import sys
import benchmark
import repository

# Oddities:
# - LPG wants at least about 384 MB to even start working on small problems.
#   If not enough RAM is provided, LPG usually quits without any message.
#   512 MB or more are preferred.
# - VHPOP is another memory hog and won't work with less than about 192 MB.
# - System R requires Prolog to be installed, which is the case on
#   alfons, turtur, ignazio and antonio, but not on all systems.
#   R might also create some output which needs to be redirected or
#   deleted (not tested), namely the files: problem, message, domain,
#   domainout.
# - System R does not seem to report failure properly.
#   Failed problems can be determined by looking at the runtime and
#   comparing it to the timeout.

TIMEOUT = 1000
MEMORY = 1024

PLANNER_PATH = path.abspath("../andere_planer")

print "Timeout: %d seconds" % TIMEOUT
print "Heap restriction: %d MB" % MEMORY
print

rep = repository.Repository()

for line in file(path.join(PLANNER_PATH, "planners.txt")):
    planner, call = line.strip().split(" ", 1)
    for domain in rep:
        for problem in domain:
            print "Running %s on %s..." % (planner, problem),
            sys.stdout.flush()
            log = benchmark.Log(problem.other_planner_log(planner))
            cmd = call.replace("$PATH", PLANNER_PATH) \
                  .replace("$DOMAIN", problem.domain_file()) \
                  .replace("$PROBLEM", problem.problem_file()) \
                  .replace("$OUTPUTFILE", log.name)
            signal, time = benchmark.run(cmd, TIMEOUT, MEMORY, log, False)
            if signal:
                print "failed!"
            else:
                print "%.2f seconds" % time
        print
