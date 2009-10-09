#! /usr/bin/env python2.5
# -*- coding: utf-8 -*-

from lmcut_tools import *

import reports
import suites

from collections import defaultdict
import csv
import os.path


REPLACEMENTS = {
    "init state": "initial state",
    "h_max": "hmax",
    "depots-ipc3": "depot",
    "logistics-aips98": "logistics98",
    "logistics-aips2000": "logistics00",
    "miconic-strips": "miconic",
    "openstacks-ipc5": "openstacks-strips",
    "pathways-ipc5": "pathways-noneg",
    "trucks-ipc5": "trucks-strips",
    "freecell-2000": "freecell",
    }

#PLANNERS = ["lmcut", "lsuda", "hhh 10k", "hhh 100k",
#            "blind", "hmax", "hsp-f", "gamer"]
PLANNERS = ["lmcut", "lsuda", "hhh 10k", "hmax",
            "blind", "gamer", "hsp-f"]
LINE_AFTER_PLANNERS = ["blind"]

def normalize(cell):
    cell = cell.strip().lower()
    cell = REPLACEMENTS.get(cell, cell)
    cell = cell.replace("_", "-")
    if cell.isdigit():
        cell = int(cell)
    elif cell.endswith("s") and cell[:-1].replace(".", "").isdigit():
        cell = float(cell[:-1])
    elif cell[:-1].replace(".", "").isdigit():
        cell = float(cell[:-1])
    return cell


def merge_headers(header1, header2):
    result = []
    for pos, cell in enumerate(header2):
        if cell in ["domain", "problem"]:
            result.append(cell)
        elif cell == "plan length":
            planner = filter(bool, header1[pos:])[0]
            result.append(cell)
        else:
            assert cell in ["initial state",
                "expanded", "evaluated", "generated",
                "search time", "total time"], cell
            result.append((planner, cell))
    return result


def parse_csv(filename):
    reader = csv.reader(open(filename))
    def read():
        return map(normalize, reader.next())
    header1 = read()
    header2 = read()
    header = merge_headers(header1, header2)
    for row in reader:
        parts = map(normalize, row)
        if any(parts):
            if parts[0] == "schedule-aips2000":
                continue ## HACK HACK HACK
            assert len(parts) <= len(header), (
                len(parts), len(header), parts, header)
            parts += [""] * (len(header) - len(parts))
            result = {}
            for key, value in zip(header, parts):
                if key in result and result[key] != "":
                    # Repeated plan length entries must be
                    # identical to first one or empty.
                    assert value in [result[key], ""], (
                            key, value, result[key], row)
                else:
                    result[key] = value
            yield result

def patch_results(data):
    for result in data:
        result = result.copy()
        domain = result["domain"]
        if domain.endswith(("-aips98", "-aips2000", "-2000",
                            "-ipc3", "-ipc4", "-ipc5")):
            domain = domain.rpartition("-")[0]
        if domain in ["openstacks", "trucks"]:
            continue ## HACK HACK HACK!!! Remove once these are OK.
        problem = result["problem"]
        if (domain in ["depot", "driverlog", "zenotravel"] or
            (domain == "freecell" and problem.startswith("pfile"))):
            problem = problem.partition(".pddl")[0]
        problem = problem.replace("pfile0", "pfile")
        problem = problem.replace("probblocks-0", "probblocks-")
        problem = problem.replace("probfreecell-0", "probfreecell-")
        problem = problem.replace("problogistics-0", "problogistics-")
        problem = problem.replace("s0", "s")
        result["domain"] = domain
        result["problem"] = problem
        for planner in PLANNERS:
            time = result[planner, "total time"]
            if time and time > 1800:
                print "%%% TIMEOUT", planner, time, \
                    result["domain"], result["problem"]
                for key in result.keys():
                    if isinstance(key, tuple) and key[0] == planner:
                        result[key] = ""
        yield result


def task_key(task):
    return str(task.domain), str(task.problem).lower()
    

suite = list(suites.generate_problems("LMCUT_SOLVABLE"))

csv_data = list(parse_csv("exp-overall.csv"))
csv_data = list(patch_results(csv_data))
csv_data = dict(((r["domain"], r["problem"]), r) for r in csv_data)

task_keys = set(map(task_key, suite))
for key in sorted(csv_data):
    if key not in task_keys:
        print "%%% unknown problem:", key
for key in sorted(task_keys):
    if key not in csv_data:
        print "%%% no data available:", key

domains = set(key[0] for key in task_keys)
total_solved = defaultdict(int)

def dump_domain_results(domain):
    solved = defaultdict(int)
    count = 0
    for key in task_keys:
        if key[0] == domain:
            count += 1
            result = csv_data.get(key)
            if not result:
                continue
            for planner in PLANNERS:
                runtime = result[planner, "total time"]
                if isinstance(runtime, (int, float)):
                    assert 0 <= runtime <= 1800, (key, planner, runtime)
                    solved[planner] += 1
                    total_solved[planner] += 1
                else:
                    assert not runtime, (key, planner, runtime)
    print r"%s {\tiny(%d)}" % (latex_format_domain(domain), count)
    parts = []
    for planner in PLANNERS:
        parts.append("& %s" % solved[planner])
    add_bold(parts, best=max)
    for part in parts:
        print part
    print r"\\"


print r"\scriptsize"
print r"\setlength{\tabcolsep}{3pt}%"
column_formats = ""
for planner in PLANNERS:
    column_formats += "r"
    if planner in LINE_AFTER_PLANNERS:
        column_formats += "|"
print r"\begin{tabular}{|l|%s|}" % column_formats
print r"\hline"
print r"\textbf{Domain}"
for planner in PLANNERS:
    print r" & \textbf{%s}" % latex_format_planner(planner)
print r"\\ \hline"
for domain in sorted(domains):
    dump_domain_results(domain)
print r"\hline"

print r"\textbf{Total}"
parts = []
for planner in PLANNERS:
    parts.append(r"& %s" % total_solved[planner])
add_bold(parts, best=max)
for part in parts:
    print part
print r"\\ \hline"

print r"\end{tabular}"
