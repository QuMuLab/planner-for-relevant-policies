#! /usr/bin/env python2.6 
# -*- coding: utf-8 -*-

import asp_fact_parser

NUM_PEGS = 4

def disk_to_num(disk):
    return int(disk[1:])

def convert_hanoi_instance(filename):
    asp_instance = asp_fact_parser.parse(filename)
   
    time_bound = len(asp_instance["time"].objects()) - 1    
    
    disks = sorted(map(disk_to_num, asp_instance["disk"].objects()))
    num_disks = len(disks) - NUM_PEGS

    print "(define (problem hanoi-problem)"
    print "  (:domain hanoi)"
    print "  (:objects "
    for disk in disks:
        print "d" + str(disk),
    print ""
    print "  )"
    print ""
      
    print "  (:init "
    for p in xrange(1, NUM_PEGS + 1):
        for d in xrange(1, num_disks + 1):
            print "(smaller d" + str(p) + " d" + str(d+NUM_PEGS) + ")",
        print ""
    print ""
    for d1 in xrange(1, num_disks + 1):
        for d2 in xrange(d1 + 1, num_disks + 1):
            print "(smaller d" + str(d1+NUM_PEGS) + " d" + str(d2+NUM_PEGS) + ")",
        print ""
    print ""
    
    clear = set(disks)
    for tup in asp_instance["on0"].tuples():
        first = disk_to_num(tup[0])
        second = disk_to_num(tup[1])
        clear.remove(second)
        print "(on d" + str(first) + " d" + str(second) + ")"
    for disk in clear:
        print "(clear d" + str(disk) + ")"

    print "  )"
    print ""
    print "  (:goal (and "

    for tup in asp_instance["ongoal"].tuples():
        first = disk_to_num(tup[0])
        second = disk_to_num(tup[1])
        print "(on d" + str(first) + " d" + str(second) + ")"

    print "  ))"
    print ""
    print ")"

   


if __name__ == "__main__":
    import sys
    convert_hanoi_instance(sys.argv[1])
