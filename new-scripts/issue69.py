#! /usr/bin/env python

import downward_experiments
from checkouts import TranslatorSvn, PreprocessorSvn, PlannerSvn

translator = TranslatorSvn(rev=3613)
preprocessor = PreprocessorSvn(rev='HEAD')

combinations = [
    (translator, preprocessor, PlannerSvn(rev=3612)),
    (translator, preprocessor, PlannerSvn(rev=3613)),
    (translator, preprocessor, PlannerSvn(rev='HEAD')),
]

downward_experiments.build_experiment(combinations)
