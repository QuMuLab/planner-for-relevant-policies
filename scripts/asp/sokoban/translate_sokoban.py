#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

import asp_fact_parser


def convert_sokoban_instance(filename):
    asp_instance = asp_fact_parser.parse(filename)

    print "(define (problem sokoban-problem)"
    print "  (:domain sokoban-sequential)"
    print "  (:objects"
    print "    dir-down - direction"
    print "    dir-left - direction"
    print "    dir-right - direction"
    print "    dir-up - direction"
    print "    player-01 - player"

    locations = set()
    box_locations = asp_instance["box"].objects()
    goal_locations = set(asp_instance["solution"].objects())

    for predicate in ["top", "right", "box", "solution", "sokoban"]:
        locations.update(asp_instance[predicate].objects())

    for location in sorted(locations):
        print "    loc-%s - location" % location

    for box_location in sorted(box_locations):
        print "    box-%s - stone" % box_location
    print "  )"

    print "  (:init"
    for location in sorted(goal_locations):
        print "    (IS-GOAL loc-%s)" % location
    for location in sorted(locations - goal_locations):
        print "    (IS-NONGOAL loc-%s)" % location

    for left_pos, right_pos in sorted(asp_instance["right"].tuples()):
        print "    (MOVE-DIR loc-%s loc-%s dir-right)" % (left_pos, right_pos)
        print "    (MOVE-DIR loc-%s loc-%s dir-left)" % (right_pos, left_pos)

    for up_pos, down_pos in sorted(asp_instance["top"].tuples()):
        print "    (MOVE-DIR loc-%s loc-%s dir-up)" % (up_pos, down_pos)
        print "    (MOVE-DIR loc-%s loc-%s dir-down)" % (down_pos, up_pos)

    player_location, = asp_instance["sokoban"].objects()
    print "    (at player-01 loc-%s)" % player_location

    for box_location in sorted(box_locations):
        print "    (at box-%s loc-%s)" % (box_location, box_location)

    for location in sorted(locations - box_locations - set([player_location])):
        print "    (clear loc-%s)" % location

    print "    (= (total-cost) 0)"
    print "  )"
    print "  (:goal (and"

    for box_location in sorted(box_locations):
        print "    (at-goal box-%s)" % box_location

    print "  ))"
    print "  (:metric minimize (total-cost))"
    print ")"


if __name__ == "__main__":
    import sys
    convert_sokoban_instance(sys.argv[1])
