
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
    faults = []

    for i in range(max_faults+1):
        faults.append(parser.Predicate("faults_%d" % i, None, []))
        p.predicates.append(faults[-1])

    for a in p.actions:
        assert isinstance(a.precondition, parser.And)
        a.precondition.args.append(parser.Primitive(started))

    p.actions.append(parser.Action('start-planning', [], None, None, parser.And(map(parser.Primitive, [started, faults[0]]))))


def convert(dom_name):

    p = load_problem(dom_name)

    while True:

        next_action = get_choice('What would you like to do?',
                                 ['See the list of actions',  # 0
                                  'Identify faulty outcomes', # 1
                                  'Set the maximum number of faults', # 2
                                  'Make the domain 1-primary normative (i.e., exactly 1 normal outcome)', # 3
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
            pass
        elif 2 == next_action:
            print
            if -1 != p.max_faults:
                print "Error: Max faults already set (reload the domain first)"
            else:
                answer = raw_input("Maximum number of faults? ")
                #try:
                choice = int(answer)
                assert choice >= 0
                add_fault_limit(p, choice)
                #except:
                #    print "\nError: You must select a number for max faults (%s)" % str(answer)
        elif 3 == next_action:
            pass
        elif 4 == next_action:
            print_domain_stats(p)
        elif 5 == next_action:
            print "\n\n-----------------\n"
            p._export_domain(sys.stdout)
            print "\n\n-----------------\n"
        elif 6 == next_action:
            pass
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
