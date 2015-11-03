
import readline, sys

from fondparser import parser, formula
from normalizer import normalize


def convert(in_dom_name, out_dom_name, width):

    print "Parsing..."

    p_fake = parser.Problem(in_dom_name)
    p = parser.Problem(in_dom_name)

    print "Augmenting..."

    nondet_actions = set()
    for a in p_fake.actions:
        normalize(a)
        if isinstance(a.effect, formula.Oneof):
            nondet_actions.add(a.name)

    def neg(pred):
        return formula.Not([pred])

    for a in p.actions:
        if a.name in nondet_actions:

            if not isinstance(a.precondition, formula.And):
                a.precondition = formula.And([a.precondition])
            if not isinstance(a.effect, formula.And):
                a.effect = formula.And([a.effect])

            if 1 == width:
                oneshot = parser.Predicate('Occ_'+a.name, a.parameters)
                p.predicates.append(oneshot)
                oneshot = formula.Primitive(oneshot)

                a.precondition.args.append(neg(oneshot))
                a.effect.args.append(oneshot)

            else:
                occs = []
                for i in range(1, width+1):
                    occs.append(parser.Predicate("Occ%d_%s" % (i,a.name), a.parameters))
                    p.predicates.append(occs[-1])
                    occs[-1] = formula.Primitive(occs[-1])

                a.precondition.args.append(neg(occs[-1]))
                a.effect.args.append(occs[0])

                for i in range(1,len(occs)):
                    a.effect.args.append(formula.When(occs[i-1], occs[i]))

    p.export(out_dom_name, None)

    print "Done!\n"


if __name__ == '__main__':
    print
    if len(sys.argv) != 4:
        print "  Usage: python %s <input domain> <output domain> <width>\n" % sys.argv[0]
        sys.exit(1)

    convert(sys.argv[1], sys.argv[2], int(sys.argv[3]))
