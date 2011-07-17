#! /usr/bin/env python

import downward_experiments
import checkouts

branch = 'svn+ssh://downward-svn/branches/translate-andrew/downward/translate'

preprocessor = checkouts.PreprocessorSvnCheckout(rev='HEAD')
planner = checkouts.PlannerSvnCheckout(rev=3842)

combinations = [
    (checkouts.TranslatorSvnCheckout(repo=branch, rev=3827),
     preprocessor, planner),
    (checkouts.TranslatorSvnCheckout(repo=branch, rev=3829),
     preprocessor, planner),
    (checkouts.TranslatorSvnCheckout(repo=branch, rev=3840),
     preprocessor, planner),
    (checkouts.TranslatorSvnCheckout(rev=4283), preprocessor, planner),
    (checkouts.TranslatorHgCheckout(),
     checkouts.PreprocessorHgCheckout(),
     checkouts.PlannerHgCheckout())
               ]

downward_experiments.build_experiment(combinations)
