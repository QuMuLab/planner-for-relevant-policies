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
    }

PLANNERS = ["lmcut", "lsuda", "hmax"]
# DOMAINS = ["blocks", "depot", "openstacks-strips"]
DOMAINS = ["blocks", "satellite", "openstacks-strips"]

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
                    if (isinstance(key, tuple) and key[0] == planner
                        and key[1] != "initial state"):
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

def select_interesting_tasks(domain):
    relevant = []
    for task in suite:
        key = task_key(task)
        if key[0] != domain:
            continue
        result = csv_data.get(key)
        if not result or not result["plan length"]:
            continue
        for planner in PLANNERS:
            if result[planner, "total time"] != "":
                relevant.append(key)
                break
    return relevant[-13:]


def dump_domain_results(domain):
    num_columns = 2 + len(PLANNERS) * 3
    print r"\multicolumn{%d}{|l|}{\tiny %s} \\ \hline" % (
        num_columns, latex_format_domain(domain))
    interesting_tasks = select_interesting_tasks(domain)

    for key in interesting_tasks:
        result = csv_data[key]
        interesting = True
        output = []
        output.append(latex_format_task(domain, key[1]))
        output.append("& %d" % result["plan length"])
        for planner in PLANNERS:
            init_h = result.get((planner, "initial state"), 999)
            expanded = result[planner, "expanded"]
            runtime = result[planner, "total time"]
            if runtime != "":
                interesting = True
                init_h = "%d" % init_h
                expanded = "%d" % expanded
                runtime = "%.2f" % runtime
            output.append(r"& %s" % init_h)
            output.append(r"& %s" % expanded)
            output.append(r"& %s" % runtime)
        add_bold(output, best=max, start=2, step=3)
        add_bold(output, best=min, start=3, step=3)
        add_bold(output, best=min, start=4, step=3)
        output.append(r"\\")
        if interesting:
            for line in output:
                print line
    print r"\hline"


print r"\scriptsize"
print r"\setlength{\tabcolsep}{2.5pt}%"
column_formats = ""
for planner in PLANNERS:
    column_formats += "rrr"
    column_formats += "|"
print r"\begin{tabular}{|r|r|%s}" % column_formats
print r"\hline"
print r"&"
for planner in PLANNERS:
    print r" & \multicolumn{3}{|c|}{\textbf{%s}}" % (
        latex_format_planner(planner))
print r"\\"
print r"\textbf{Inst.}"
print r"& $h^*$"
for planner in PLANNERS:
    print r" & $h$"
    print r" & Exp."
    print r" & Time"
print r"\\ \hline"
for domain in DOMAINS:
    dump_domain_results(domain)
print r"\end{tabular}"
