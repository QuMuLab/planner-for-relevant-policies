#! /usr/bin/env python

import sys
import subprocess
import itertools

configs = ['3612-ou', '3613-ou', '5272-ou']
attributes = ['expansions', 'search_time', ]
domains = ['airport', 'blocks', 'depot', 'driverlog', 'elevators-opt08-strips',
           'elevators-sat08-strips', 'freecell', 'grid', 'gripper',
           'logistics00', 'logistics98', 'miconic', 'mprime', 'mystery',
           'openstacks-opt08-strips', 'openstacks-sat08-strips',
           'openstacks-strips', 'parcprinter-08-strips', 'pathways-noneg',
           'pegsol-08-strips', 'pipesworld-notankage', 'pipesworld-tankage',
           'psr-small', 'rovers', 'satellite', 'scanalyzer-08-strips',
           'sokoban-opt08-strips', 'sokoban-sat08-strips', 'tpp',
           'transport-opt08-strips', 'transport-sat08-strips', 'trucks-strips',
           'woodworking-opt08-strips', 'woodworking-sat08-strips',
           'zenotravel']

def make_plot(params):
    print ' '.join(params)
    ret = subprocess.call(params)
    if not ret == 0:
        sys.exit(1)

for cfg1, cfg2 in itertools.combinations(configs, 2):
    for attribute in attributes:
        attr_params = ['./downward-reports.py', 'exp-js-issue69-eval/',
                '-a', attribute, '-r', 'scatter', '-c', cfg1 + ',' + cfg2,
                '--res', 'problem']
        make_plot(attr_params)
        for domain in domains:
            params = attr_params + ['--suite', domain]
            make_plot(params)
