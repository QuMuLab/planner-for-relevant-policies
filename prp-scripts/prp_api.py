
import os

USAGE_STRING = """
python prp_api.py <command> <solution file>

  <solution file> should be the output of translate_policy.py.

  <commmand> should be one of the following:

           display: Display the parsed policy (just for debugging purposes)

     count-circuit: Create the CNF version of the policy to count the successful states.
                    Creates files <solution file>.map and <solution file>.cnf

    action-circuit: Create the CNF version of the policy's circuit representation
                    that has inputs for the fluents and outputs for the actions.
                    Creates the same files as the count-circuit command.
"""


DEBUG = False


# http://stackoverflow.com/questions/1456373/two-way-reverse-map
class TwoWayDict(dict):
    def __setitem__(self, key, value):
        # Remove any previous connections with these values
        if key in self:
            del self[key]
        if value in self:
            del self[value]
        dict.__setitem__(self, key, value)
        dict.__setitem__(self, value, key)

    def __delitem__(self, key):
        dict.__delitem__(self, self[key])
        dict.__delitem__(self, key)

    def __len__(self):
        """Returns the number of connections"""
        return dict.__len__(self) // 2


class PRPPolicy:

    def __init__(self, sol):

        with open(sol) as f:
            data = filter(lambda x: x!='', [l.strip() for l in f.readlines()])

        self.mapping = TwoWayDict()
        self.policy = []
        self.fsap = {}

        doPol = False
        doFSAP = False

        line = data.pop(0)
        assert line == 'Mapping:'
        while data:
            line = data.pop(0)
            if doFSAP:
                cond = set(line.split(': ')[1].split('/'))
                line = data.pop(0)
                act = line.split('Forbid: ')[1].strip()
                self.fsap[act] = self.fsap.get(act, []) + [cond]
            elif doPol:
                if 'FSAP:' == line:
                    doFSAP = True
                    continue
                cond = set(line.split(': ')[1].split('/'))
                line = data.pop(0)
                act = line.split(' /')[0].split('Execute: ')[1].strip()
                self.policy.append((cond, act))
            else:
                if 'Policy:' == line:
                    doPol = True
                    continue
                self.mapping[line.split('\t')[0]] = line.split('\t ')[-1]

    def get_action(state):
        # Assumes that anything negated is explicitly in the state
        #  which is a set of strings. E.g., 'not(onground())'
        for (cond,act) in self.policy:
            if cond <= state:
                ok = True
                for de in self.fsap[act]:
                    if de <= state:
                        ok = False
                if ok:
                    return act
        return None

def display(p):
    from pprint import pprint

    print
    print "Mapping:"
    pprint(p.mapping)

    print
    print "Policy:"
    pprint(p.policy)

    print
    print "FSAP:"
    pprint(p.fsap)
    print

def action_circuit(p, mapfile, cnffile):
    from krrt.sat import CNF

    CLAUSES = []

    def partial_state_clause(ps):
        aux = '+'.join(sorted(ps))
        CLAUSES.append(map(CNF.Not, ps) + [aux])
        for f in ps:
            CLAUSES.append([CNF.Not(aux), f])
        return aux

    for psap in p.policy:
        print partial_state_clause(psap[0])
        print psap[1]
        print


def count_circuit(p, mapfile, cnffile):
    from krrt.sat import CNF

    CLAUSES = []
    FLUENTS = set()

    def fluentvar(f):
        if '!' == f[0]:
            FLUENTS.add(CNF.Variable(f[1:]))
            return CNF.Not(CNF.Variable(f[1:]))
        else:
            FLUENTS.add(CNF.Variable(f))
            return CNF.Variable(f)

    def neg(l):
        if isinstance(l, CNF.Not):
            return l.var
        else:
            return CNF.Not(l)

    # For every <ps,a>, a->ps
    for psap in p.policy:
        for f in psap[0]:
            CLAUSES.append([CNF.Not(psap[1]), fluentvar(f)])

    # To avoid projection: For every <ps,a>, ps->a
    for psap in p.policy:
        CLAUSES.append([psap[1]] + map(CNF.Not, map(fluentvar, psap[0])))

    # For every <de,a>, de->!a
    for act in p.fsap:
        for de in p.fsap[act]:
            CLAUSES.append(map(neg, map(fluentvar, de)) + [CNF.Not(act)])

    # At least one action is applicable
    CLAUSES.append(set([psap[1] for psap in p.policy]))

    if DEBUG:
        print '\n'.join(map(str, CLAUSES))

    F = CNF.Formula(CLAUSES)
    F.writeMapping(mapfile)
    F.writeCNF(cnffile)

    print "\nsharpSAT Command: ./bin/sharpSAT %s\n" % cnffile

    #print "\nD# Command: ./dsharp -projectionViaPriority -priority %s %s\n" % \
    #      (','.join(map(str, sorted([F.mapping[f] for f in FLUENTS]))), cnffile)

if __name__ == '__main__':
    if len(os.sys.argv) != 3:
        print "\nError with input."
        print USAGE_STRING
        os.sys.exit(1)

    print "Parsing solution..."
    p = PRPPolicy(os.sys.argv[2])

    if 'display' == os.sys.argv[1]:
        display(p)
    elif 'count-circuit' == os.sys.argv[1]:
        count_circuit(p, os.sys.argv[2]+'.map', os.sys.argv[2]+'.cnf')
    elif 'action-circuit' == os.sys.argv[1]:
        action_circuit(p, os.sys.argv[2]+'.map', os.sys.argv[2]+'.cnf')
    else:
        print "\nError with input."
        print USAGE_STRING
        os.sys.exit(1)
