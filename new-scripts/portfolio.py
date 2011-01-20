#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

import pprint
import sys


properties = ["config", "domain", "problem",
              "status", "total_time", "cost"]


def parse():
    data = {}
    for line in open(sys.argv[1]):
        left, match, right = line.partition("=")
        left = left.strip()
        right = right.strip()
        if not match:
            assert line.startswith("[")
            if not line.startswith("[["):
                if data:
                    yield data
                data = {}
        elif left in properties:
            assert left not in data
            data[left] = right


def massage_entry(entry):
    assert "config" in entry, entry
    assert "domain" in entry, entry
    assert "problem" in entry, entry
    assert "status" in entry, entry
    config = entry["config"]
    domain = entry["domain"]
    problem = entry["problem"]
    status = entry["status"]
    assert status in ["'ok'", "'unsolved'"], entry

    if "08" in domain and "0000" in config:
        # M&S config with no action cost support
        # print "IGNORED:", entry
        time = None
        cost = None
    elif status == "'ok'":
        assert "total_time" in entry, entry
        assert "cost" in entry, entry
        time = float(entry["total_time"])
        assert time <= 1800, entry
        cost = int(entry["cost"])
    else:
        assert "cost" not in entry, entry
        time = None
        cost = None
    return dict(
        config=config,
        problem=(domain, problem),
        time=time,
        cost=cost)


def main():
    configs = set()
    problems = set()
    results = {}

    for entry in parse():
        entry = massage_entry(entry)
        config = entry["config"]
        problem = entry["problem"]
        configs.add(config)
        problems.add(problem)
        results[config, problem] = (entry["time"], entry["cost"])

    for config in configs:
        for problem in problems:
            if (config, problem) not in results:
                print "MISSING:", config, problem
                results[config, problem] = (None, None)

    # Count total problems solved, check that all plans have same
    # quality, and discard the plan costs.
    total_solved = 0
    for problem in problems:
        best_cost = None
        for config in configs:
            config_time, config_cost = results[config, problem]
            if config_cost is not None:
                if best_cost is None:
                    best_cost = config_cost
                else:
                    assert config_cost == best_cost, (
                        problem, config_cost, best_cost)
            results[config, problem] = config_time
        if best_cost is not None:
            total_solved += 1

    print len(results), "results"
    print len(configs), "configs"
    print len(problems), "problems"
    assert len(results) == len(configs) * len(problems)
    print total_solved, "problems solved by someone"
    for config in sorted(configs):
        num_solved = len([problem for problem in problems
                          if results[config, problem] is not None])
        print num_solved, "problems solved by", config
    # pprint.pprint(results)

if __name__ == "__main__":
    main()


