
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

class State:
    def __init__(self, fluents):
        self.fluents = set(fluents)
        self.hash_val = hash(','.join(sorted(list(map(str, fluents)))))

    def __hash__(self):
        return self.hash_val

    def __eq__(self, other):
        return self.hash_val == other.hash_val

    def is_goal(self, goal):
        return goal <= self.fluents


class VALAction:
    def __init__(self, prec, eff):
        self.pres = set(prec)
        self.adds = set(filter(lambda x: x > 0, eff))
        self.dels = set([-1 * i for i in filter(lambda x: x < 0, eff)])


def validate(dfile, pfile, sol, val):

    problem = grounder.GroundProblem(dfile, pfile)

    val.load(sol)

    fluents = {}
    unfluents = ['NULL']
    index = 1
    for f in problem.fluents:
        fluents[str(f)] = index
        fluents["not(%s)" % str(f)] = -1 * index
        unfluents.append(str(f))
        index += 1

    actions = {}
    for op in problem.operators:
        actions[op.name] = [VALAction(_convert_conjunction(fluents, op.precondition),
                                      _convert_conjunction(fluents, eff))
                            for eff in flatten(op)]
        #print "\n%s\n%s" % (op.name, '\n'.join(map(str, actions[op.name])))

    init_state = State(_convert_conjunction(fluents, problem.init))
    goal_state = State([-1])
    goal_fluents = _convert_conjunction(fluents, problem.goal)

    open_list = [init_state]

    G = nx.DiGraph()
    G.add_node(init_state)
    G.add_node(goal_state)

    print "\nStarting the FOND simulation..."

    while open_list:

        u = open_list.pop(0)
        assert u in G

        #print "\nHandling state:"
        #print _state_string(unfluents, u)

        a = val.next_action(u)
        for outcome in actions[a]:
            v = progress(u, outcome)
            if v.is_goal(goal_fluents):
                G.add_edge(u, goal_state, action=a)
            else:
                if v not in G:
                    G.add_node(v)
                    open_list.append(v)
                G.add_edge(u, v, action=a)


    # Analyze the final controller
    print "\nSimulation finished!"
    print "\n-{ Controller Statistics }-"
    print "Nodes: %d" % G.number_of_nodes()
    print "Edges: %d" % G.number_of_edges()



def _convert_conjunction(mapping, conj):
    assert isinstance(conj, And)
    return [mapping[str(f)] for f in conj.args]

def _state_string(mapping, state):
    return '\n'.join([mapping[i] for i in state.fluents])

def progress(s, o):
    assert o.pres <= s.fluents
    return State(((s.fluents - o.dels) | o.adds))


if __name__ == '__main__':
    try:
        (dom, prob, sol, interp) = os.sys.argv[1:]
    except:
        print "\nError with input."
        print USAGE_STRING
        os.sys.exit(1)

    validate(dom, prob, sol, importlib.import_module("validators.%s" % interp))
