#! /usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
from glob import glob
import os.path
from os.path import join as joinpath, split as splitpath


def read_runtime(filename):
    for line in open(filename):
        parts = line.split()
        if len(parts) == 5 and parts[0] == "Done!":
            return float(parts[1].strip("[s"))
    return None
    

def read_results(dirnames):
    results = defaultdict(dict)
    for dirname in dirnames:
        pattern = joinpath(dirname, "results", "translate",
                           "*", "*", "translate.log")
        for result_file in glob(pattern):
            runtime = read_runtime(result_file)
            result_dir, _ = splitpath(result_file)
            domain_dir, problem = splitpath(result_dir)
            _, domain = splitpath(domain_dir)
            task = "%s:%s" % (domain, problem)
            results[task][dirname] = runtime
    return results


def statistics(dirname, results):
    def report(msg):
        print "[%s] %s" % (dirname, msg)
    total_time = 0
    solved = 0
    unsolved = 0
    for task, result in sorted(results.iteritems()):
        time = result.get(dirname)
        if time is None:
            unsolved += 1
            report("%s is unsolved" % task)
        else:
            solved += 1
            total_time += time
    report("%10d solved" % solved)
    report("%10d unsolved" % unsolved)
    report("%10.3f total time" % total_time)
    print


def compare_pair(dirname1, dirname2, results):
    print "Comparing %s to %s..." % (dirname1, dirname2)
    commonly_solved_times = []
    differences = []
    ratios = []
    ROUND_UP_TO = 0.1
    for task, result in sorted(results.iteritems()):
        time1 = result.get(dirname1)
        time2 = result.get(dirname2)
        if time1 is not None and time2 is not None:
            time1 = max(time1, ROUND_UP_TO)
            time2 = max(time2, ROUND_UP_TO)
            triple = (task, time1, time2)
            differences.append((time2 - time1, triple))
            ratios.append((time1 / time2, triple))
    top_ten("top ten absolute improvements of %s compared to %s:",
            "%8.3f sec", dirname1, dirname2, differences)
    top_ten("top ten speedup ratios of %s compared to %s:",
            "%8.3f", dirname1, dirname2, ratios)


def top_ten(title, pattern, dirname1, dirname2, values):
    print
    title = title % (dirname1, dirname2)
    print title
    best_ten = sorted(values, reverse=True)[:10]
    worst_ten = sorted(values, reverse=False)[:10]
    for top_ten in [best_ten, worst_ten]:
        print "-" * len(title)
        for value, (task, time1, time2) in top_ten:
            value_text = pattern % value
            print "%s  %-30s  [%s: %s; %s: %s]" % (
                value_text, task, dirname1, time1, dirname2, time2)


def compare_results(dirnames, results):
    for dirname in dirnames:
        statistics(dirname, results)

    for dirname1 in dirnames:
        for dirname2 in dirnames:
            if dirname1 != dirname2:
                compare_pair(dirname1, dirname2, results)


if __name__ == "__main__":
    import sys
    dirnames = map(os.path.normpath, sys.argv[1:])
    results = read_results(dirnames)
    compare_results(dirnames, results)
