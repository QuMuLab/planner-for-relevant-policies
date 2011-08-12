#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

def convert_solitaire_solution(filename):
    text = open(filename).read().strip()
    if text:
        last_dest = ""
        step = 1
        for action in text.split("\n"):
            action = action.strip()
            action = action[1:-1]
            args = action.split()
            coordinates = args[1].split("-")
            coordinates_direction = args[2].split("-")
            time_step = args[5][1:]
            direction = "left"
            if coordinates[1] < coordinates_direction[1]:
                direction = "right"
            elif coordinates[2] < coordinates_direction[2]:
                direction = "down"
            elif coordinates[2] > coordinates_direction[2]:
                direction = "up"
            print "move(%s,%s,%s,%s)." % (time_step,direction,coordinates[1],coordinates[2])
    
if __name__ == "__main__":
    import sys
    convert_solitaire_solution(sys.argv[1])
