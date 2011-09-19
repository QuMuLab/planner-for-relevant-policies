#! /usr/bin/env python

"""
This script shows the usage of the checkouts module together with the
downward_experiments module. Together those modules can be used to create
experiments that compare the performance of Fast Downward components. You can
easily compare different revisions of the translate, preprocess and search
component.
"""

import downward_experiments
from checkouts import Translator, Preprocessor, Planner

# This combination shows the available parameters and their possible values
combinations = [
    (Translator(repo='../', rev='e9845528763d'),
     Preprocessor(repo='http://hg.fast-downward.org', rev='tip', dest='repo1'),
     Planner(rev='WORK')),
]

# These combinations show how to have multiple copies of the same revision
# This can be useful e.g. if you want to check the impact of Makefile options
combinations = [
    (Translator(), Preprocessor(), Planner(rev=1600, dest='copy1')),
    (Translator(), Preprocessor(), Planner(rev=1600, dest='copy2')),
]

# These combinations show how to check the impacts of your uncommited changes
combinations = [
    (Translator(rev='tip'), Preprocessor(rev='tip'), Planner(rev='tip')),
    (Translator(rev='WORK'), Preprocessor(rev='WORK'), Planner(rev='WORK')),
]

downward_experiments.build_experiment(combinations)
