#! /usr/bin/env python2.6 
# -*- coding: utf-8 -*-

import asp_fact_parser

def const_to_num(disk):
    return int(disk[1:])

def convert_knight_instance(filename):
    asp_instance = asp_fact_parser.parse(filename)
   
    size = const_to_num(list(asp_instance["size"].objects())[0])
    
    given_moves = set(map(lambda l: tuple(map(lambda x: const_to_num(x) - 1, l)),  asp_instance["givenmove"].tuples()))
    if len(given_moves) == 0: # If there are no given moves, we might as well start with this move
        given_moves.add( (1,1,2,3) )
    
    
    given_to = {}
    given_from = {}
    
    for (x1, y1, x2, y2) in given_moves:
        given_from[(x1,y1)] = (x2,y2)
        given_to[(x2,y2)] = (x1,y1)
    
    start_pos = given_from.keys()[0]
    
    visited = {}
    did = {}
    
    print "begin_metric"
    print "0"
    print "end_metric"
    print "begin_variables"
    print 2 + (size * size) + len(given_moves)
    print "posX",size,-1
    print "posY",size,-1
    v = 2
    for x in xrange(size):
        for y in xrange(size):
            print "visited_" + str(x) + "_" + str(y),2,-1
            visited[(x,y)] = v
            v = v + 1
    for (m1,m2,m3,m4) in given_moves:
        print "didmove_" + str(m1) + "_" + str(m2) + "_" + str(m3) + "_" + str(m4),2,-1
        did[(m1,m2,m3,m4)] = v
        v = v + 1
    print "end_variables"
    
    print "begin_state"
    print start_pos[0]
    print start_pos[1]
    for x in xrange(size):
        for y in xrange(size):
            print 0
    for (m1,m2,m3,m4) in given_moves:
        print 0
    print "end_state"
    
    print "begin_goal"
    print 2 + (size * size) + len(given_moves)
    print 0, start_pos[0]
    print 1, start_pos[1]
    for var_num in xrange((size * size) + len(given_moves)):
        print var_num + 2, 1
    print "end_goal"
    
    print "NUM_OPS"    
    
    for x1 in xrange(size):
        for y1 in xrange(size):
            for dx,dy in [(1,2),(1,-2),(-1,2),(-1,-2),(2,1),(2,-1),(-2,1),(-2,-1)]:
                x2 = x1 + dx
                y2 = y1 + dy
                if (0 <= x2 < size) and (0 <= y2 < size) and ( (not (x1,y1) in given_from and not (x2,y2) in given_to) or (x1,y1,x2,y2) in given_moves):
                    print "begin_operator"
                    print "move",x1,y1,x2,y2
                    print 0
                    if (x1,y1,x2,y2) in given_moves:
                        print 4
                    else:
                        print 3
                    print 0,0,x1,x2
                    print 0,1,y1,y2
                    print 0,visited[(x2,y2)],0,1
                    if (x1,y1,x2,y2) in given_moves:
                        print 0, did[(x1,y1,x2,y2)], -1, 1
                    print 0
                    print "end_operator"
                    
    print 0                
    
    
    
    
    
   


if __name__ == "__main__":
    import sys
    convert_knight_instance(sys.argv[1])
