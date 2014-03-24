
import os, importlib

from parser import grounder
from parser.formula import *
from normalizer import flatten

import networkx as nx

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
        #print "\n%s\n%s" % (op.name, '\n'.join(map(str, actions[op.name])))

    fluents = {}
    unfluents = []
    index = 0
    for f in problem.fluents:
        fluents[str(f)] = index
        unfluents.append(str(f))
        index += 1

    assert isinstance(problem.init, And)
    init_state = ','.join(set(map(str, [fluents[str(f)] for f in problem.init.args])))

    open_list = [init_state]
    closed_list = set()

    G = nx.DiGraph()

    print "\nStarting the FOND simulation..."

    while open_list:
        n = open_list.pop(0)
        if n not in closed_list:
            closed_list.add(n)


            print "\nHandling state:"
            print state_string(unfluents, n)

def state_string(mapping, state):
    return '\n'.join([mapping[int(i)] for i in state.split(',')])

def _encode_fluent(mapping, fluent):
    return

if __name__ == '__main__':
    try:
        (dom, prob, sol, interp) = os.sys.argv[1:]
    except:
        print "\nError with input."
        print USAGE_STRING
        os.sys.exit(1)

    validate(dom, prob, sol, importlib.import_module("validators.%s" % interp))
