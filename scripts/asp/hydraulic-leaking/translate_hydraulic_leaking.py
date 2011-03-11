#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

import asp_fact_parser


def convert_hydraulic_leaking_instance(filename):
    asp_instance = asp_fact_parser.parse(filename)

    print "(define (problem hydraulic-leaking-problem)"
    print "  (:domain hydraulic-leaking)"
    print "  (:objects"

    for tank in sorted(asp_instance["tank"].objects()):
        print "    %s - tank" % tank
    for jet in sorted(asp_instance["jet"].objects()):
        print "    %s - jet" % jet
    for junction in sorted(asp_instance["junction"].objects()):
        print "    %s - junction" % junction
    for valve in sorted(asp_instance["valve"].objects()):
        print "    %s - valve" % valve

    print "  )"
    print "  (:init"

    for linked in sorted(asp_instance["link"].tuples()):
        print "    (link %s %s %s)" % (linked[0], linked[1], linked[2])

    for valve in sorted(asp_instance["leaking"].objects()):
        print "    (leaking %s)" % valve

    for tank in sorted(asp_instance["full"].objects()):
        print "    (full %s)" % tank
        print "    (pressurized %s)" % tank

    print "    (= (total-cost) 0)"
    print "  )"
    print "  (:goal (and"

    for goal in sorted(asp_instance["goal"].objects()):
        print "    (pressurized %s)" % goal

    print "  ))"
    print "  (:metric minimize (total-cost))"
    print ")"

if __name__ == "__main__":
    import sys
    convert_hydraulic_leaking_instance(sys.argv[1])
