
import os


USAGE_STRING = """
python prp-policy-api.py <solution>

  Only used for testing the loading of a PRP policy.
"""

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

if __name__ == '__main__':
    if len(os.sys.argv) != 2:
        print "\nError with input."
        print USAGE_STRING
        os.sys.exit(1)

    print "Parsing solution..."
    p = PRPPolicy(os.sys.argv[1])

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
