
import readline, sys

from fondparser import parser, formula
from fondparser.action import Action
from normalizer import normalize

# PRP style
# PATTERN = '<name>_DETDUP_<num>'

# FIP style
PATTERN = 'D_<num>_<name>'

def determinize(ifile, ofile):

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
                name = a.name.join(PATTERN.split('<name>'))
                name = str(i+1).join(name.split('<num>'))
                a2 = Action(name, a.parameters, a.precondition, a.observe, a.effect.args[i])
                p.actions.append(a2)
        else:
            p.actions.append(a)

    p.export(ofile, None)


if __name__ == '__main__':
    print
    if len(sys.argv) != 3:
        print "  Usage: python %s <fond domain> <determinized domain>\n" % sys.argv[0]
        sys.exit(1)

    determinize(sys.argv[1], sys.argv[2])
