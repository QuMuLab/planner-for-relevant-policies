#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

import downward_experiments
from checkouts import Translator, Preprocessor, Planner


combinations = [
    (Translator(rev="default", dest="default"),
     Preprocessor(rev="default", dest="default"),
     Planner(rev="default", dest="default")),
    (Translator(rev="issue278", dest="issue278"),
     Preprocessor(rev="default", dest="default"),
     Planner(rev="default", dest="default")),
]


downward_experiments.build_experiment(combinations)
