#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

import asp_fact_parser


def convert_sokoban_instance(filename):
    asp_instance = asp_fact_parser.parse(filename)

    print "(define (problem airport-problem)"
    print "  (:domain pseudo-airport)"
    print "  (:objects"
    
    for location in asp_instance["location"].objects():
        print "    loc-%s - location" % location
    
    for passenger in asp_instance["passenger"].objects():
        print "    %s - passenger" % passenger
    
    for vehicle in asp_instance["vehicle"].tuples():
        print "    %s - vehicle" % vehicle[0]
    
    max_distance = max(int(driveway[2]) for driveway in asp_instance["driveway"].tuples())
    print "    dist-0 - distance"
    for index_distance in range(max_distance):
        print "    dist-%s - distance" % str(index_distance+1)
    
    max_overall_fuel = max(int(vehicle[1]) for vehicle in asp_instance["vehicle"].tuples())
    print "    fuel-0 - gas_level"
    for index_fuel in range(max_overall_fuel):
        print "    fuel-%s - gas_level" % str(index_fuel+1)
    
    print "  )"
    print "  (:init"
    
    for gas in asp_instance["gasstation"].objects():
        print "    (gas loc-%s)" % gas
    
    for driveway in asp_instance["driveway"].tuples():
        print "    (driveway loc-%s loc-%s dist-%s)" % (driveway[0],driveway[1],driveway[2])
        print "    (driveway loc-%s loc-%s dist-%s)" % (driveway[1],driveway[0],driveway[2])
        
    for vehicle in asp_instance["vehicle"].tuples():
        print "    (max_fuel %s fuel-%s)" % (vehicle[0], vehicle[1])
        
    for init_gas in asp_instance["init_gas"].tuples():
        print "    (current_fuel %s fuel-%s)" % (init_gas[0], init_gas[1])
        
    for init_at in asp_instance["init_at"].tuples():
        print "    (at %s loc-%s)" % (init_at[0], init_at[1])
        
    distances = [int(driveway[2]) for driveway in asp_instance["driveway"].tuples()]
    for index_distance in range(max_distance+1)[1:]:
        if(index_distance in distances):
            for index_fuel in range(max_overall_fuel+1):
                if index_fuel >= index_distance:
                    print "    (fuel_lost dist-%s fuel-%s fuel-%s)" % (index_distance, index_fuel, str(index_fuel-index_distance))
        
    
    print "  )"
    print "  (:goal (and "
    
    airports = asp_instance["airport"].tuples()
    for init_at in asp_instance["init_at"].tuples():
        if init_at[0][0] == "p":
            if init_at[1] == airports[0][0]:
                print "    (at %s loc-%s)" % (init_at[0], airports[1][0])
            else:
                print "    (at %s loc-%s)" % (init_at[0], airports[0][0])    
    
    print "  )  )\n)"


if __name__ == "__main__":
    import sys
    convert_sokoban_instance(sys.argv[1])
