#!/usr/bin/python

from sys import argv, stderr, stdout

if (len(argv) != 2):
	stderr.write("usage: %s problemfile.pddl\n" % (argv[0]))
	exit(1)

with open(argv[1]) as problem_file:
	lines = problem_file.readlines()

i = 0
while (not lines[i].startswith(')')):
	i += 1
i += 1
while (not lines[i].startswith('(')):
	i += 1

for line in lines[i:]:
	if ('goal-reward' in line or 'metric' in line):
		continue
	stdout.write(line)
