
import pddl

def get_name(old):
    if 'DETDUP' not in old:
        return old
    orig = old.split('_DETDUP')[0]
    num = int(old.split('_')[-1]) + 1
    return "D_%d_%s" % (num, orig)

def get_atom(atom):
    if atom.negated:
        return "(not %s)" % get_atom(atom.positive())
    
    if len(atom.args) == 0:
        return "(%s)" % atom.predicate
    else:
        return "(%s %s)" % (atom.predicate, ' '.join(atom.args))

def print_parameters(params):
    mapping = {}
    for p in params:
        mapping.setdefault(p.type, []).append(p.name)
    print "  :parameters (",
    for t in mapping.keys():
        print "%s - %s" % (' '.join(mapping[t]), t),
    print ")"

def print_precondition(precond, start_string = "  :precondition"):
    print start_string,
    if precond.__class__ == pddl.conditions.Conjunction:
        print "(and %s)" % ' '.join([get_atom(a) for a in precond.parts])
    else:
        print get_atom(precond)

def print_effects(eff, precond):
    # Duplicate the precondition if there are no effects
    if len(eff) == 0:
        print_precondition(precond, "  :effect")
    elif len(eff) == 1:
        print "  :effect %s" % get_atom(eff[0].literal)
    else:
        print "  :effect (and %s)" % ' '.join([get_atom(a.literal) for a in eff])
    
task = pddl.open()

for action in task.actions:
    print "\n(:action %s" % get_name(action.name)
    print_parameters(action.parameters)
    print_precondition(action.precondition)
    print_effects(action.effects, action.precondition)
    print ")"

print ""
