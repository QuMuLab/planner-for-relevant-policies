#! /usr/bin/env python2.5
# -*- coding: utf-8 -*-

import sas_tasks

class Statistics(object):
    def __init__(self, task):
        vars = task.variables
        ranges = [var.range for var in vars]
        self.name = task.name
        self.no_vars = len(vars)
        self.no_derived_vars = len(
            [var for var in vars if var.is_axiom])
        self.no_propositions = sum(ranges)
        self.avg_range = float(sum(ranges)) / len(ranges)
        self.max_range = max(ranges)
        self.no_goals = len(task.goals)
        self.no_operators = len(task.operators)
        self.no_effects = sum(len(op.effects) for op in task.operators)
        self.no_axioms = len(task.axioms)

    def print_human_friendly(self):
        print "%s:" % self.name
        for entry in self._entries():
            print entry
        print

    def print_grep_friendly(self):
        for entry in self._entries():
            print "%s: %s" % (self.name, entry)

    def _entries(self):
        yield "%8d variables" % self.no_vars
        yield "%8d derived variables" % self.no_derived_vars
        yield "%8d propositions" % self.no_propositions
        yield "%8.2f average variable range" % self.avg_range
        yield "%8d maximal variable range" % self.max_range
        yield "%8d goals" % self.no_goals
        yield "%8d operators" % self.no_operators
        yield "%8d operator effects" % self.no_effects
        yield "%8d axioms" % self.no_axioms



if __name__ == "__main__":
    import sys
    sas_file, key_file = sys.argv[1:]
    task = sas_tasks.read(sas_file, key_file)
    statistics = Statistics(task)
    statistics.print_human_friendly()
