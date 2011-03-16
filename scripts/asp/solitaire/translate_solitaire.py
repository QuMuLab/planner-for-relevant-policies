#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

import asp_fact_parser


def convert_sokoban_instance(filename):
    asp_instance = asp_fact_parser.parse(filename)

    print "(define (problem solitaire-problem)"
    print "  (:domain pegsolitaire-sequential)"
    print "  (:objects"
    
    locations = sorted(asp_instance["full"].tuples() + asp_instance["empty"].tuples())
    
    for loc1, loc2 in locations:
        print "    pos-%s-%s - location" % (loc1,loc2)
    
    print "    t0 - time-step"
    for time in sorted(asp_instance["time"].objects(), key=int):
        print "    t%s - time-step" % time
    
    print "  )"
    print "  (:init"
    print "    (at-time t0)"
    print "    (= (total-cost) 0)"
    
    for time in range(len(asp_instance["time"].objects())):
        print "    (consecutive t%s t%s)" % (time, time+1)
    
    for loc1,loc2 in asp_instance["full"].tuples():
        print "    (occupied pos-%s-%s)" % (loc1,loc2)
    
    for loc1,loc2 in asp_instance["empty"].tuples():
        print "    (free pos-%s-%s)" % (loc1,loc2)
    
    max_height = int(max(locations)[0])
    max_width = max(int(location[1]) for location in locations)
    
    for index_height in range(max_height)[1:]:
        for index_width in range(max_width)[1:]:
            if [str(index_height-1),str(index_width)] in locations and [str(index_height),str(index_width)] in locations and [str(index_height+1),str(index_width)] in locations:
                print "    (IN-LINE pos-%s-%s pos-%s-%s pos-%s-%s)" % (index_height-1,index_width,index_height,index_width,index_height+1,index_width)
                print "    (IN-LINE pos-%s-%s pos-%s-%s pos-%s-%s)" % (index_height+1,index_width,index_height,index_width,index_height-1,index_width)
            if [str(index_height),str(index_width-1)] in locations and [str(index_height),str(index_width)] in locations and [str(index_height),str(index_width+1)] in locations:
                print "    (IN-LINE pos-%s-%s pos-%s-%s pos-%s-%s)" % (index_height,index_width-1,index_height,index_width,index_height,index_width+1)
                print "    (IN-LINE pos-%s-%s pos-%s-%s pos-%s-%s)" % (index_height,index_width+1,index_height,index_width,index_height,index_width-1)
    
    print "  )"
    print "  (:goal (at-time t%s))" % len(asp_instance["time"].objects())
    print "  (:metric minimize (total-cost))"
    print ")"


if __name__ == "__main__":
    import sys
    convert_sokoban_instance(sys.argv[1])
