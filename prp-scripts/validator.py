
import os, importlib

from parser import grounder
from normalizer import flatten

USAGE_STRING = """
Usage: python validator.py <domain> <problem> <solution> <interpreter>

    <domain> and <problem> are the original FOND domain and problem files.
    <solution> is a file that contains the FOND plan.
    <interpreter> is the module for the <solution> interpreter.
        validators/<interpreter>.py should exist and contain
        (at least) two functions: load and next_action

    Example usage: python validator.py domain.pddl p3.pddl policy.out prp
        """

def validate(dfile, pfile, sol, val):

    problem = grounder.GroundProblem(dfile, pfile)

    val.load(sol)

    actions = {}
    for op in problem.operators:
        actions[op.name] = flatten(op)

    open_list = problem.init


if __name__ == '__main__':
    try:
        (dom, prob, sol, interp) = os.sys.argv[1:]
    except:
        print "\nError with input."
        print USAGE_STRING
        os.sys.exit(1)

    validate(dom, prob, sol, importlib.import_module("validators.%s" % interp))
