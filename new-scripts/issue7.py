#! /usr/bin/env python

import downward_experiments
from checkouts import Translator, Preprocessor, Planner
from checkouts import TranslatorSvn, PreprocessorSvn, PlannerSvn

branch = 'svn+ssh://downward-svn/branches/translate-andrew/'

preprocessor = PreprocessorSvn(rev='HEAD')
planner = PlannerSvn(rev=3842)

combinations = [
    (TranslatorSvn(repo=branch, rev=3827), preprocessor, planner),
    (TranslatorSvn(repo=branch, rev=3829), preprocessor, planner),
    (TranslatorSvn(repo=branch, rev=3840), preprocessor, planner),
    (TranslatorSvn(rev=4283), preprocessor, planner),
    (Translator(), Preprocessor(), Planner())
]

downward_experiments.build_experiment(combinations)
