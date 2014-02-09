#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

def convert_sokoban_solution(filename):
    text = open(filename).read().strip()
    if text:
        last_dest = ""
        step = 1
        for action in text.split("\n"):
            action = action.strip()
            action = action[1:-1]
            args = action.split()
            operator = args[0].split("-")
            if operator[0] == "move" and last_dest != "":
                print "%s,%s)." % (last_dest,step)
                last_dest = ""
                step += 1
            elif operator[0] == "push":
                if last_dest != "":
                    print "%s,%s)." % (last_dest,step)
                    step += 1
                sys.stdout.write("push(" + args[4][5:] + "," + operator[1] + ",")
                last_dest = args[5][5:]
            elif operator[0] == "chain":
                last_dest = args[5][5:]
        print "%s,%s)." % (last_dest,step)
    
if __name__ == "__main__":
    import sys
    convert_sokoban_solution(sys.argv[1])
