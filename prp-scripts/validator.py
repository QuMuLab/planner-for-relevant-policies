
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
        self.eff = eff


def validate(dfile, pfile, sol, val):

    problem = grounder.GroundProblem(dfile, pfile)

    fluents = {}
    unfluents = {}
    index = 1
    for f in problem.fluents:
        fluents[str(f)] = index
        fluents["not(%s)" % str(f)] = -1 * index
        unfluents[index] = str(f)
        unfluents[-1 * index] = "not(%s)" % str(f)
        index += 1

    actions = {}
    for op in problem.operators:
        actions[op.name] = [VALAction(_convert_conjunction(fluents, op.precondition),
                                      _convert_conjunction(fluents, eff))
                            for eff in flatten(op)]
        #print "\n%s\n%s" % (op.name, '\n'.join(map(str, actions[op.name])))

    init_state = State(_convert_conjunction(fluents, problem.init))
    goal_state = State([-1])
    goal_fluents = set(_convert_conjunction(fluents, problem.goal))

    open_list = [init_state]

    G = nx.DiGraph()
    G.add_node(init_state, label="I")
    G.add_node(goal_state, label="G")

    val.load(sol, fluents)

    print "\nStarting the FOND simulation..."

    while open_list:

        u = open_list.pop(0)
        assert u in G

        #print "\nHandling state:"
        #print _state_string(unfluents, u)

        a = val.next_action(u)
        i = 0
        for outcome in actions[a]:

            v = progress(u, outcome)
            i += 1

            if v.is_goal(goal_fluents):
                v = goal_state
            elif v not in G:
                G.add_node(v, label="")
                open_list.append(v)

            G.add_edge(u, v, label="%s (%d)" % (a, i))


    # Analyze the final controller
    print "\nSimulation finished!\n"
    print "\n-{ Controller Statistics }-\n"
    print "\t Nodes: %d" % G.number_of_nodes()
    print "\t Edges: %d" % G.number_of_edges()
    print "\tStrong: %s" % str(0 == len(list(nx.simple_cycles(G))))
    print " Strong Cyclic: %s" % str(G.number_of_nodes() == len(nx.single_source_shortest_path(G.reverse(), goal_state)))

    nx.write_dot(G, 'graph.dot')

    with open('action.map', 'w') as f:
        for a in actions:
            f.write("\n%s:\n" % a)
            i = 0
            for outcome in actions[a]:
                i += 1
                f.write("%d: %s\n" % (i, str([unfluents[fl] for fl in outcome.eff])))

    print "\n   Plan output: graph.dot"
    print "Action mapping: action.map\n"



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
