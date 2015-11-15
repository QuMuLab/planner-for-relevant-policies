
import readline, sys

from fondparser import parser, formula
from fondparser.action import Action
from normalizer import normalize

PATTERNS = {'PRP': '<name>_DETDUP_<num>',
            'FIP': 'D_<num>_<name>'}

PLANNER_INDEX = {'PRP':0, 'FIP':1} # They each count from different bases

def determinize(ptype, ifile, ofile):

    pattern = PATTERNS[ptype]

    p_fake = parser.Problem(ifile)
    p = parser.Problem(ifile)

    nondet_actions = set()
    for a in p_fake.actions:
        normalize(a)
        if isinstance(a.effect, formula.Oneof):
            nondet_actions.add(a.name)

    def neg(pred):
        return formula.Not([pred])

    p.actions = []
    for a in p_fake.actions:
        if a.name in nondet_actions:
            for i in range(len(a.effect.args)):
                name = a.name.join(pattern.split('<name>'))
                name = str(i+PLANNER_INDEX[ptype]).join(name.split('<num>'))
                a2 = Action(name, a.parameters, a.precondition, a.observe, a.effect.args[i])
                p.actions.append(a2)
        else:
            p.actions.append(a)

    p.export(ofile, None)


if __name__ == '__main__':
    print
    if (len(sys.argv) != 4) or (sys.argv[1] not in ['FIP', 'PRP']):
        print "  Usage: python %s [FIP|PRP] <fond domain> <determinized domain>\n" % sys.argv[0]
        sys.exit(1)

    determinize(sys.argv[1], sys.argv[2], sys.argv[3])
