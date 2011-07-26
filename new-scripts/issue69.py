#! /usr/bin/env python

import downward_experiments
import checkouts

combinations = [
    (checkouts.TranslatorSvn(rev=3613),
     checkouts.PreprocessorSvn(rev='HEAD'),
     checkouts.PlannerSvn(rev=3612)),
    (checkouts.TranslatorSvn(rev=3613),
     checkouts.PreprocessorSvn(rev='HEAD'),
     checkouts.PlannerSvn(rev=3613)),
    (checkouts.TranslatorSvn(rev=3613),
     checkouts.PreprocessorSvn(rev='HEAD'),
     checkouts.PlannerSvn(rev='HEAD')),
               ]

downward_experiments.build_experiment(combinations)
