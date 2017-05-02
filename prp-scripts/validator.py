
import os, importlib

from fondparser import grounder
from fondparser.formula import *
from normalizer import flatten

import networkx as nx
from networkx.drawing.nx_pydot import write_dot

USAGE_STRING = """
Usage: python validator.py <domain> <problem> <solution> <interpreter>

    <domain> and <problem> are the original FOND domain and problem files.
    <solution> is a file that contains the FOND plan.
    <interpreter> is the module for the <solution> interpreter.
        validators/<interpreter>.py should exist and contain
        (at least) two functions: load and next_action

    Example usage: python validator.py domain.pddl p3.pddl policy.out prp

    Caveats:
      * Equality predicates are ignored in the grounding / simulation.

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
    def __init__(self, prec, effs, name, mapping):
        self.name = name
        self.ppres = set(filter(lambda x: x > 0, prec))
        self.npres = set([-1 * i for i in filter(lambda x: x < 0, prec)])
        self.effs = effs
        self.mapping = mapping

    def __str__(self):
        return "%s: +Pre = %s / -Pre = %s / Effs = %s" % (self.name, \
                        str([self.mapping[fl] for fl in self.ppres]), \
                        str([self.mapping[fl] for fl in self.npres]), \
                        str(["(%s --> %s)" % (','.join([self.mapping[fl] for fl in c]), ','.join([self.mapping[fl] for fl in e])) for (c,e) in self.effs]))


def validate(dfile, pfile, sol, val):

    print "\nParsing the problem..."

    problem = grounder.GroundProblem(dfile, pfile)

    fluents = {}
    unfluents = {}
    index = 1
    for f in problem.fluents:
        fluents[str(f).lower()] = index
        fluents["not(%s)" % str(f).lower()] = -1 * index
        unfluents[index] = str(f).lower()
        unfluents[-1 * index] = "not(%s)" % str(f).lower()
        index += 1

    actions = {}
    for op in problem.operators:
        if '_' == op.name[-1]:
            op_name = op.name[:-1].lower()
        else:
            op_name = op.name.lower()

        actions[op_name] = [VALAction(_convert_conjunction(fluents, op.precondition),
                                      _convert_cond_effect(fluents, eff), op_name, unfluents)
                            for eff in flatten(op)]

        #print "\n%s\n%s" % (op.name, '\n'.join(map(str, actions[op.name])))

    init_state = State(_convert_conjunction(fluents, problem.init))
    goal_state = State([-1])
    goal_fluents = set(_convert_conjunction(fluents, problem.goal))

    open_list = [init_state]

    nodes = {init_state: 1, goal_state: 2}
    node_index = 3

    G = nx.MultiDiGraph()
    G.add_node(1, label="I")
    G.add_node(2, label="G")

    val.load(sol, fluents)

    print "\nStarting the FOND simulation..."

    unhandled = []

    while open_list:

        u = open_list.pop(0)
        assert nodes[u] in G

        #print "\n--------\nHandling state:"
        #print _state_string(unfluents, u)

        a = val.next_action(u)

        if not a:
            G.node[nodes[u]]['label'] = 'X'
            unhandled.append(u)
        else:
            i = 0
            for outcome in actions[a]:

                v = progress(u, outcome, unfluents)
                #print "\nNew state:"
                #print _state_string(unfluents, v)
                i += 1

                if v.is_goal(goal_fluents):
                    v = goal_state
                elif v not in nodes:
                    nodes[v] = node_index
                    node_index += 1
                    G.add_node(nodes[v], label="")
                    open_list.append(v)

                G.add_edge(nodes[u], nodes[v], label="%s (%d)" % (a, i))


    # Analyze the final controller
    print "\nSimulation finished!\n"
    print "\n-{ Controller Statistics }-\n"
    print "\t Nodes: %d" % G.number_of_nodes()
    print "\t Edges: %d" % G.number_of_edges()
    print "     Unhandled: %d" % len(unhandled)
    print "\tStrong: %s" % str(0 == len(list(nx.simple_cycles(G))))
    print " Strong Cyclic: %s" % str(G.number_of_nodes() == len(nx.single_source_shortest_path(G.reverse(), nodes[goal_state])))

    write_dot(G, 'graph.dot')

    with open('action.map', 'w') as f:
        for a in actions:
            f.write("\n%s:\n" % a)
            i = 0
            for outcome in actions[a]:
                i += 1
                f.write("%d: %s\n" % (i, " / ".join(["%s -> %s" % (map(str, [unfluents[fl] for fl in c]), map(str, [unfluents[fl] for fl in e])) for (c,e) in outcome.effs])))

    if len(unhandled) > 0:
        with open('unhandled.states', 'w') as f:
            for s in unhandled:
                f.write("\n%s\n" % _state_string(unfluents, s))

    print "\n     Plan output: graph.dot"
    print "  Action mapping: action.map"
    if len(unhandled) > 0:
        print "Unhandled states: unhandled.states"

    print


def _convert_cond_effect(mapping, eff):
    if isinstance(eff, And):
        return [_create_cond(mapping, f) for f in filter(lambda x: '=' not in str(x), eff.args)]
    elif isinstance(eff, Primitive) or (isinstance(eff, Not) and isinstance(eff.args[0], Primitive)):
        return [_create_cond(mapping, eff)]
    elif isinstance(eff, When):
        return [_create_cond(mapping, eff)]
    else:
        assert False, "Error: Tried converting a non-standard effect: %s" % str(eff)

def _create_cond(mapping, eff):
    if isinstance(eff, Primitive) or (isinstance(eff, Not) and isinstance(eff.args[0], Primitive)):
        return (set(), set([mapping[str(eff).lower()]]))
    elif isinstance(eff, When):
        return (set(_convert_conjunction(mapping, eff.condition)), set(_convert_conjunction(mapping, eff.result)))
    else:
        assert False, "Error: Tried converting a non-standard single effect: %s" % str(eff)

def _convert_conjunction(mapping, conj):
    if isinstance(conj, And):
        return [mapping[str(f).lower()] for f in filter(lambda x: '=' not in str(x), conj.args)]
    elif isinstance(conj, Primitive) or (isinstance(conj, Not) and isinstance(conj.args[0], Primitive)):
        return [mapping[str(conj).lower()]]
    else:
        assert False, "Error: Tried converting a non-standard conjunction: %s" % str(conj)

def _state_string(mapping, state):
    return '\n'.join(sorted([mapping[i] for i in state.fluents]))

def progress(s, o, m):
    assert o.ppres <= s.fluents and 0 == len(o.npres & s.fluents), \
        "Failed to progress %s:\nPrecondition: %s\nState:\n%s" % \
        (o.name, str(o.pres), _state_string(m, s))

    #print "\nProgressing the following operator:"
    #print (o)

    adds = set()
    dels = set()
    for eff in o.effs:
        negeff = set(filter(lambda x: x < 0, eff[0]))
        poseff = eff[0] - negeff
        negeff = set(map(lambda x: x * -1, negeff))
        if (poseff <= s.fluents) and 0 == len(negeff & s.fluents):
            for reff in eff[1]:
                if reff < 0:
                    dels.add(reff * -1)
                else:
                    adds.add(reff)

    if 0 != len(adds & dels):
        print "Warning: Conflicting adds and deletes on action %s" % str(o)

    return State(((s.fluents - dels) | adds))


if __name__ == '__main__':
    try:
        (dom, prob, sol, interp) = os.sys.argv[1:]
    except:
        print "\nError with input."
        print USAGE_STRING
        os.sys.exit(1)

    validate(dom, prob, sol, importlib.import_module("validators.%s" % interp))
