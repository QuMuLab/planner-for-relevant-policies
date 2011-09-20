#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

import downward_experiments
from checkouts import Translator, Preprocessor, Planner


combinations = [
    (Translator(rev="default", dest="default"),
     Preprocessor(rev="default", dest="default"),
     Planner(rev="default", dest="default")),
    (Translator(rev="default", dest="default"),
     Preprocessor(rev="default", dest="default"),
     Planner(rev="issue276", dest="issue276")),
]


downward_experiments.build_experiment(combinations)
