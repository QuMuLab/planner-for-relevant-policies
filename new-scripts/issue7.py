#! /usr/bin/env python

from downward_experiments import *

branch = 'svn+ssh://downward-svn/branches/translate-andrew/downward/translate'

preprocessor = PreprocessorSvnCheckout()
planner = PlannerSvnCheckout(rev=3842)

combinations = [
    (TranslatorSvnCheckout(repo=branch, rev=3827), preprocessor, planner),
    (TranslatorSvnCheckout(repo=branch, rev=3829), preprocessor, planner),
    (TranslatorSvnCheckout(repo=branch, rev=3840), preprocessor, planner),
    (TranslatorSvnCheckout(rev=4283), preprocessor, planner),
               ]
               
build_experiment(combinations)
