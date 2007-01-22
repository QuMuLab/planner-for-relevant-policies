#! /usr/bin/env python

from paths import DOWNWARD_DIR

import getopt
import os
import sys

import benchmark
import repository

class Solver:
    def __init__(self, algorithm, problem, timeout, memory):
        self.algorithm = algorithm
        self.problem = problem
        self.time = timeout
        self.timeout = timeout
        self.memory = memory
        self.result_files = repository.ResultFiles(algorithm, problem)
    def _run_cmd(self, cmd, verbose, logname):
        sig, secs = benchmark.run(cmd, self.time, self.memory,
                                  benchmark.Log(logname), verbose)
        self.time -= int(secs)
        return (sig == 0, secs)
    def translate(self, verbose=True):
        cmd = os.path.join(DOWNWARD_DIR, "translate", "translate.py")
        cmd = " ".join((cmd, self.problem.domain_file(), self.problem.problem_file()))
        if False:
            ## This is a weird HACK to silence problems when bytecode already exists.
            ## This might be related to a recently fixed bug in the translator, where
            ## Atom instances with identical hash value would falsely be considered equal.
            ## If so, this should no longer be needed, so it is deactivated for the time being.
            translator_path = os.path.join(DOWNWARD_DIR, "translate")
            os.system("rm -f %s/*.pyc %s/pddl/*.pyc" % (translator_path, translator_path))
        ok, secs = self._run_cmd(cmd, verbose, self.result_files.translate_log())
        if ok:
            os.system("mv output.sas %s" % self.result_files.translate_out())
        return ok, secs
    def preprocess(self, verbose=True):
        cmd = os.path.join(DOWNWARD_DIR, "preprocess", "preprocess")
        cmd = "%s < %s" % (cmd, self.result_files.translate_out())
        ok, secs = self._run_cmd(cmd, verbose, self.result_files.preprocess_log())
        if ok:
            os.system("mv output %s" % self.result_files.preprocess_out())
        return ok, secs
    def search(self, verbose=True):
        cmd = os.path.join(DOWNWARD_DIR, "search", "search-%s" % self.algorithm)
        old_dir = os.curdir
        os.chdir(os.path.join(DOWNWARD_DIR, "search"))
        cmd = "%s < %s" % (cmd, self.result_files.preprocess_out())
        os.chdir(old_dir)
        ok, secs = self._run_cmd(cmd, verbose, self.result_files.search_log())
        if ok:
            os.system("mv sas_plan %s" % self.result_files.search_out())
        return ok, secs
    def solve(self, verbose=False):
        log = benchmark.Log(self.result_files.global_log())
        print >> log, "Domain:  %s" % self.problem.domain
        print >> log, "Problem: %s" % self.problem.problem
        
        ok, s1 = self.translate(verbose)
        if ok:
            ok, s2 = self.preprocess(verbose)
        if ok:
            ok, s3 = self.search(verbose)
        print >> log, ("\nSummary:\n" +
                       "  Timeout:       %7.2f seconds\n" +
                       "  Max memory:    %7.2f MB\n") \
                       % (self.timeout, self.memory)
        if ok:
            print >> log, ("  Translation:   %7.2f seconds\n" +
                           "  Preprocessing: %7.2f seconds\n" +
                           "  Searching:     %7.2f seconds\n" +
                           "  Total:         %7.2f seconds\n") \
                           % (s1, s2, s3, s1 + s2 + s3)
            return True
        else:
            print >> log, "  Available resources exhausted.\n"
            return False

def solve(problem, timeout, memory):
    Solver(problem, timeout, memory).solve()

def usage():
    print """Usage: solver.py [options] [domain [problem]]
        Possible options:
        -v, --verbose            Verbose output.
        -t, --translate          Only run the translation phase.
        -p, --preprocess         Only run the preprocessing phase.
        -s, --search             Only run the search phase.
        -a ALG, --algorithm ALG  Use alternative search algorithm ALG
                                 for the search phase.

        Options -t, -p, -s are mutually exclusive. If several of these
        are specified, later arguments take precedence.
        If domain and problem are specified, attempt that problem.
        If only domain is specified, attempt all problems in that domain.
        If neither domain nor problem is specified, attempt all problems."""

def main():
    # TIMEOUT = 330
    TIMEOUT = 1830
    MEMORY = 512

    try:
        opts, args = getopt.getopt(sys.argv[1:], "vtpsa:",
                                   ["verbose", "translate", "preprocess", "search",
                                    "algorithm="])
        if len(args) > 2:
            raise getopt.GetoptError("too many positional arguments")
    except getopt.GetoptError, e:
        print "Error: %s." % str(e).capitalize()
        usage()
        sys.exit(2)

    verbose = False
    task = Solver.solve
    algorithm = "downward"
    for opt, arg in opts:
        if opt in ("-v", "--verbose"):
            verbose = True
        if opt in ("-t", "--translate"):
            task = Solver.translate
        if opt in ("-p", "--preprocess"):
            task = Solver.preprocess
        if opt in ("-s", "--search"):
            task = Solver.search
        if opt in ("-a", "--algorithm"):
            algorithm = arg
        
    if len(args) == 0:
        problems = [prob for dom in repository.Repository() for prob in dom]
    elif len(args) == 1:
        problems = [prob for prob in repository.Domain(args[0])]
    else:
        problems = [repository.Problem(*args)]

    for problem in problems:
        print "Working on %s..." % problem
        solver = Solver(algorithm, problem, TIMEOUT, MEMORY)
        task(solver, verbose)

if __name__ == "__main__":
    main()
