#! /usr/bin/env python

import sys
import subprocess

configs = ['bjolp', 'autotune', 'lmcut', 'selmax', 'lama-2011-nonunit',
           'lama-2011-unit']

def make_report(params):
    print ' '.join(params)
    ret = subprocess.call(params)
    if not ret == 0:
        sys.exit(1)

for config in configs:
    for res in ['domain', 'problem']:
        params = ['./downward-reports.py', 'exp-js-102-eval/',
                  '--filter', 'config:contains:%s' % config, '--outfile',
                  'reports/issue102-abs-%s-%s.html' % (config, res[0]),
                  '--res', res]
        make_report(params)
