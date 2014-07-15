
import readline, sys

from fondparser import parser


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

def convert(dom_name):
    print "Parsing..."
    p = parser.Problem(dom_name)
    p.max_faults = -1

    print "Normalizing..."

    print "Ready!"

    while True:

        next_action = get_choice('What would you like to do?',
                                 ['See the list of actions',  # 0
                                  'Identify faulty outcomes', # 1
                                  'Set the maximum number of faults', # 2
                                  'Make the domain 1-primary normative (i.e., exactly 1 normal outcome)', # 3
                                  'Show domain statistics', # 4
                                  'Print the domain', # 5
                                  'Save the domain',  # 6
                                  'Quit'])            # 7

        if 0 == next_action:
            pass
        elif 1 == next_action:
            pass
        elif 2 == next_action:
            pass
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
            print
            return


if __name__ == '__main__':
    print
    if len(sys.argv) != 2:
        print "\n  Usage: python %s <domain>\n" % sys.argv[0]
        sys.exit(1)

    convert(sys.argv[1])
