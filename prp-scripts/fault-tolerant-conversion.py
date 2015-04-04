
import readline, sys

from fondparser import parser
from normalizer import normalize


def get_choice(query, options):
    not_valid = True
    while not_valid:
        print
        print query
        i = 1
        for opt in options:
            print " %d. %s" % (i, opt)
            i += 1
        answer = raw_input("? ")
        try:
            choice = int(answer)
            assert 0 < choice < i
            not_valid = False
        except:
            print "\nError: You must select a number between 1 and %d" % (i-1)
    return choice - 1


def print_domain_stats(p):
    print
    print "Actions:\t %d" % len(p.actions)
    print "Max faults:\t %d" % p.max_faults
    print "1-Normative:\t %s" % str(is_normative(p))


def load_problem(dom_name):
    print "Parsing..."
    p = parser.Problem(dom_name)
    p.max_faults = -1

    print "Normalizing..."
    for a in p.actions:
        normalize(a)

    print "Ready!"

    return p


def add_fault_limit(p, max_faults):

    p.max_faults = max_faults
    started = parser.Predicate("started", None, [])
    p.predicates.append(started)
    p.faults = []

    for i in range(max_faults+1):
        p.faults.append(parser.Predicate("faults_%d" % i, None, []))
        p.predicates.append(p.faults[-1])

    for a in p.actions:
        if isinstance(a.precondition, parser.Primitive) or isinstance(a.precondition, parser.Not):
            a.precondition = parser.And([a.precondition])
        assert isinstance(a.precondition, parser.And)
        a.precondition.args.append(parser.Primitive(started))

        if isinstance(a.effect, parser.Oneof):
            for eff in a.effect.args:
                eff.faulty = False

    p.actions.append(parser.Action('start-planning',
                                   [],
                                   parser.Not([parser.Primitive(started)]),
                                   None,
                                   parser.And(map(parser.Primitive, [started, p.faults[0]]))))


def pick_faulty_outcome(p, action):
    effs = filter(lambda eff: not eff.faulty, action.effect.args)
    if len(effs) < 1:
        print "Error: No more normal effects to become faulty."
        return False
    elif len(effs) == 1:
        print "\nWarning: You are about to make the final effect faulty."
        if 1 == get_choice('Continue?', ['Yes', 'No']):
            return False

    print "\nYou have the following choice of outcomes:"
    for i in range(len(effs)):
        print "\n\t--- %d ---" % (i+1)
        print str(effs[i])
    print

    outcome_choice = get_choice('Which outcome?', ['' for i in range(len(effs))] + ['Cancel'])

    if outcome_choice == len(effs):
        print "Cancelling..."
        return False

    eff = effs[outcome_choice]

    make_outcome_faulty(p, eff)

    print "Done..."
    return


def make_outcome_faulty(p, eff):
    eff.faulty = True
    assert isinstance(eff, parser.And)

    old_effect = parser.And(eff.args)
    eff.args = []

    eff.args.append(parser.When(parser.Not([parser.Primitive(p.faults[-1])]), old_effect))

    for i in range(p.max_faults):
        eff.args.append(parser.When(parser.Primitive(p.faults[i]),
                                    parser.And([parser.Primitive(p.faults[i+1]),
                                                parser.Not([parser.Primitive(p.faults[i])])])))


def action_valid(a):
    if not isinstance(a.effect, parser.Oneof):
        return False
    for eff in a.effect.args:
        if not eff.faulty:
            return True
    return False


def is_normative(p):
    if -1 == p.max_faults:
        return all([not isinstance(a.effect, parser.Oneof) for a in p.actions])

    for a in p.actions:
        if isinstance(a.effect, parser.Oneof):
            return 1 == len(filter(lambda eff: not eff.faulty, a.effect.args))


def convert(dom_name):

    p = load_problem(dom_name)

    while True:

        next_action = get_choice('What would you like to do?',
                                 ['See the list of actions',   # 0
                                  'Set the maximum number of faults', # 1
                                  'Identify a faulty outcome', # 2
                                  'Make the domain 1-primary normative\n     (i.e., exactly 1 normal outcome per action)', # 3
                                  'Show domain statistics', # 4
                                  'Print the domain', # 5
                                  'Save the domain',  # 6
                                  'Reload the domain',# 7
                                  'Quit'])            # 8

        if 0 == next_action:
            print
            print "Actions:"
            for a in p.actions:
                print " - %s" % a.name
            print
        elif 1 == next_action:
            print
            if -1 != p.max_faults:
                print "Error: Max faults already set (reload the domain first)"
            else:
                answer = raw_input("Maximum number of faults? ")
                try:
                    choice = int(answer)
                    if choice < 1:
                        print "\nError: You must select a positive number for max faults."
                    else:
                        add_fault_limit(p, choice)
                except ValueError:
                    print "\nError: You must select a number for max faults (%s)" % str(answer)
        elif 2 == next_action:
            print
            if -1 == p.max_faults:
                print "Error: You must first set the maximum number of faults."
                continue

            suitable_actions = filter(action_valid, p.actions)

            if not suitable_actions:
                print "Error: No actions available to make faulty."
                continue

            action_choice = get_choice('Which action?', [a.name for a in suitable_actions])
            action = p.actions[action_choice]

            if not isinstance(action.effect, parser.Oneof):
                print "Error: You can only make non-deterministic effects faulty."
            else:
                pick_faulty_outcome(p, action)
        elif 3 == next_action:
            print
            if -1 == p.max_faults:
                print "Error: You must first set the maximum number of faults."
                continue

            suitable_actions = filter(action_valid, p.actions)

            if not suitable_actions:
                print "Error: No actions available to make faulty."
                continue

            for act in suitable_actions:
                effs = filter(lambda eff: not eff.faulty, act.effect.args)
                if len(effs) > 1:
                    print "\nMaking action %s faulty." % act.name
                    print "You have the following choice of outcomes:"
                    for i in range(len(effs)):
                        print "\n\t--- %d ---" % (i+1)
                        print str(effs[i])
                    print

                    outcome_choice = get_choice('Which is the normal (i.e., non-faulty) outcome?', ['' for i in range(len(effs))])

                    for i in range(len(effs)):
                        if i != outcome_choice:
                            make_outcome_faulty(p, effs[i])

        elif 4 == next_action:
            print_domain_stats(p)
        elif 5 == next_action:
            print "\n\n-----------------\n"
            p._export_domain(sys.stdout)
            print "\n\n-----------------\n"
        elif 6 == next_action:
            print
            answer = raw_input("What filename would you like to use? ")
            p.export(answer, '')
        elif 7 == next_action:
            p = load_problem(dom_name)
        elif 8 == next_action:
            print
            return


if __name__ == '__main__':
    print
    if len(sys.argv) != 2:
        print "  Usage: python %s <domain>\n" % sys.argv[0]
        sys.exit(1)

    convert(sys.argv[1])
