#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

import downward_experiments
from checkouts import Translator, Preprocessor, Planner


combinations = [
    (Translator(rev="default"),
     Preprocessor(rev="default"),
     Planner(rev="default")),
    (Translator(rev="issue28"),
     Preprocessor(rev="issue28"),
     Planner(rev="issue28")),
]


downward_experiments.build_experiment(combinations)
