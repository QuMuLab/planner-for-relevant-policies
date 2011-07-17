#! /usr/bin/env python

import downward_experiments
import checkouts

combinations = [
    (checkouts.Translator(rev='e9845528763d'),
     checkouts.Preprocessor(rev='WORK', repo='http://hg.fast-downward.org'),
     checkouts.Planner(rev='TIP'))]

downward_experiments.build_experiment(combinations)
