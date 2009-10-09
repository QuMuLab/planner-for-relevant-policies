#! /usr/bin/env python2.5
# -*- coding: utf-8 -*-

from lmcut_tools import *

import reports
import suites

from collections import defaultdict
import csv
import os.path


REPLACEMENTS = {
    "add_h_max (aaai05)": "HBG",
    "coles-etal": "CFLS",
    "hla": "K&D",
    # "lsuda": "K&D old",
    "h_max": "hmax",
    "depots": "depot",
    "freecell-2000": "freecell",
    "logistics-1998": "logistics98",
    "logistics-2000": "logistics00",
    "m10(miconic)": "miconic",
    "openstacks": "openstacks-strips",
    "pathways": "pathways-noneg",
    "pw-no-tankage": "pipesworld-notankage",
    "pw-tankage": "pipesworld-tankage",
    "trucks": "trucks-strips",
    "zeno-travel": "zenotravel",
    }

HEURISTICS = ["h+", "hmax", "HBG", "CFLS", "K&D", "lmcut"]

def normalize(cell):
    cell = cell.strip().lower()
    cell = REPLACEMENTS.get(cell, cell)
    cell = cell.replace("_", "-")
    if cell.isdigit():
        cell = int(cell)
    return cell


def parse_csv(filename):
    reader = csv.reader(open(filename))
    header = map(normalize, reader.next())
    for row in reader:
        if row:
            parts = map(normalize, row)
            assert len(parts) <= len(header)
            parts += [""] * (len(header) - len(parts))
            yield dict(zip(header, parts))


def filter_results(data):
    for result in data:
        ## TODO: Remove this hack once openstacks-strips is complete.
        if (result["domain"] == "openstacks-strips" and
            result["problem"] >= "p08.pddl"):
            continue
        if isinstance(result["h+"], int):
            yield result
        else:
            assert result["h+"] in ["", "fail", "infinite"]



def patch_results(data):
    for result in data:
        if (result["domain"] in ["depot", "driverlog", "zenotravel"] or
            (result["domain"] == "freecell" and
             result["problem"].startswith("pfile"))):
            result["problem"] = result["problem"].partition(".pddl")[0]


import paths
orig_results_dir = paths.RESULTS_DIR
paths.RESULTS_DIR = orig_results_dir.replace("lmcut", "hplus")
suite = suites.generate_problems("LMCUT_SOLVABLE")
## TODO: Remove this hack once openstacks-strips is complete.
suite = [task for task in suite
         if (task.domain != "openstacks-strips" or
             task.problem < "p08.pddl")]
hplus_results = reports.collect_results(suite)
paths.RESULTS_DIR = orig_results_dir

suite = list(suites.generate_problems("LMCUT_SOLVABLE"))
## TODO: Remove this hack once openstacks-strips is complete.
suite = [task for task in suite
         if (task.domain != "openstacks-strips" or
             task.problem < "p08.pddl")]

lmcut_results = reports.collect_results(suite)

csv_data = list(parse_csv("exp-accuracy.csv"))
csv_data = list(filter_results(csv_data))
patch_results(csv_data)


def task_key(task):
    return str(task.domain), str(task.problem).lower()
    

hplus_data = dict((task_key(r.problem), r) for r in hplus_results)
lmcut_data = dict((task_key(r.problem), r) for r in lmcut_results)
csv_data = dict(((r["domain"], r["problem"]), r) for r in csv_data)

assert set(hplus_data) == set(lmcut_data), (
    set(hplus_data) - set(lmcut_data),
    set(lmcut_data) - set(hplus_data))
good_keys = set(hplus_data)

for csv_key in sorted(csv_data):
    if csv_key not in good_keys:
        print "*** WARNING %s\n" % (csv_key,)

data = {}
for task in suite:
    key = task_key(task)
    hplus_result = hplus_data[key]
    lmcut_result = lmcut_data[key]
    if hplus_result.solved:
        hplus = hplus_result.length
        lmcut = lmcut_result.init_h
        assert key in csv_data, "missing task: %s" % (key,)
        csv_hplus = csv_data[key]["h+"]
        assert hplus == csv_hplus, "bad h+ data: %s" % (key,)
        csv_data[key]["lmcut"] = lmcut
        data[key] = csv_data[key]
    elif key in csv_data and isinstance(csv_data[key]["h+"], int):
        # print "*** EXTERNAL RESULT %s\n" % (key,)
        hplus = csv_data[key]["h+"]
        lmcut = lmcut_result.init_h
        csv_data[key]["lmcut"] = lmcut
        data[key] = csv_data[key]


hplus_keys = sorted(data)
domains = set(key[0] for key in hplus_keys)

heur_total_errors = defaultdict(int)
heur_total_approx = defaultdict(int)
heur_total_counts = defaultdict(int)

def dump_domain_results(domain, predicate):
    totals = defaultdict(int)
    missing = defaultdict(lambda: False)
    count = 0
    for key in hplus_keys:
        if key[0] == domain:
            count += 1
            result = data[key]
            line = str(key)
            hplus_val = result["h+"]
            for heur in HEURISTICS:
                hval = result[heur]
                if isinstance(hval, int):
                    line += " %s=%d" % (heur, hval)
                    totals[heur] += hval
                    heur_total_errors[heur] += (hplus_val - hval)
                    heur_total_approx[heur] += float(hval) / hplus_val
                    heur_total_counts[heur] += 1
                else:
                    line += " %s=None" % heur
                    missing[heur] = True
            # print line
    output = []
    output.append(r"%s {\tiny(%d)}" % (
        latex_format_domain(domain), count))
    for heur in HEURISTICS:
        if missing[heur]:
            text = "n/a"
        else:
            text = "%.2f" % (float(totals[heur]) / count)
        output.append("& %s" % text)
    output.append(r"\\")
    add_bold(output, best=max, start=2)
    lmcut_error = float(totals["h+"] - totals["lmcut"]) / count
    if predicate(lmcut_error):
        for line in output:
            print line

print r"\scriptsize"
print r"\setlength{\tabcolsep}{3pt}%"
print r"\begin{tabular}{|l|r|" + "r" * (len(HEURISTICS) - 1) + r"|}"
print r"\hline"
print r"\textbf{Domain}"
for heur in HEURISTICS:
    print r" & \textbf{%s}" % latex_format_heur(heur)
print r"\\ \hline\hline"
for predicate in [
    lambda err: err == 0,
    lambda err: 0 < err <= 1.0,
    lambda err: 1.0 < err]:
    for domain in sorted(domains):
        dump_domain_results(domain, predicate)
    print r"\hline"
print r"\multicolumn{2}{|l|}{\textbf{avg.~additive error compared to \hplus}}"

parts = []
for heur in HEURISTICS[1:]:
    total_error = heur_total_errors[heur]
    total_count = heur_total_counts[heur]
    error = "%.2f" % (float(total_error) / total_count)
    parts.append(r"& %s" % error)
add_bold(parts, best=min)
for part in parts:
    print part
    
print r"\\"
parts = []
print r"\multicolumn{2}{|l|}{\textbf{avg.~relative error compared to \hplus}}"
for heur in HEURISTICS[1:]:
    total_approx = heur_total_approx[heur]
    total_count = heur_total_counts[heur]
    percentage = "%.1f\%%" % (100 * (1 - float(total_approx) / total_count))
    parts.append(r"& %s" % percentage)
add_bold(parts, best=min)
for part in parts:
    print part
print r"\\ \hline"

print r"\end{tabular}"
