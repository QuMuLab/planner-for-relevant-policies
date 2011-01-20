#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

import pprint
import sys


class Results(object):
    def __init__(self, file):
        self.configs = set()
        self.problems = set()
        self.data = {}

        self._parse_entries(file)
        self._add_missing_entries()
        assert len(self.data) == len(self.configs) * len(self.problems)
        self._verify_optimality_and_discard_costs()

    def _parse_entries(self, file):
        for entry in self._parse(file):
            entry = self._massage_entry(entry)
            config = entry["config"]
            problem = entry["problem"]
            self.configs.add(config)
            self.problems.add(problem)
            self.data[config, problem] = (entry["time"], entry["cost"])

    def _parse(self, file):
        properties = ["config", "domain", "problem",
                      "status", "total_time", "cost"]
        data = {}
        for line in file:
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

    def _massage_entry(self, entry):
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

    def _add_missing_entries(self):
        for config in self.configs:
            for problem in self.problems:
                if (config, problem) not in self.data:
                    print "MISSING:", config, problem
                    self.data[config, problem] = (None, None)

    def _verify_optimality_and_discard_costs(self):
        for problem in self.problems:
            costs = set(self.data[config, problem][1]
                        for config in self.configs)
            costs.discard(None)
            assert len(costs) <= 1, (problem, sorted(costs))
            for config in self.configs:
                self.data[config, problem] = self.data[config, problem][0]

    def _total_solved(self):
        total_solved = 0
        for problem in self.problems:
            if any([config for config in self.configs
                    if self.data[config, problem] is not None]):
                total_solved += 1
        return total_solved

    def dump_statistics(self):
        print len(self.data), "results"
        print len(self.configs), "configs"
        print len(self.problems), "problems"
        print self._total_solved(), "problems solved by someone"
        for config in sorted(self.configs):
            num_solved = len([problem for problem in self.problems
                              if self.data[config, problem] is not None])
            print num_solved, "problems solved by", config


def main():
    results = Results(open(sys.argv[1]))
    results.dump_statistics()
    # pprint.pprint(results.data)


if __name__ == "__main__":
    main()
