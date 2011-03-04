#! /usr/bin/env python

import downward_experiments
import checkouts

combinations = [
    (checkouts.TranslatorSvnCheckout(rev=3613),
     checkouts.PreprocessorSvnCheckout(rev='HEAD'),
     checkouts.PlannerSvnCheckout(rev=3612)),
    (checkouts.TranslatorSvnCheckout(rev=3613),
     checkouts.PreprocessorSvnCheckout(rev='HEAD'),
     checkouts.PlannerSvnCheckout(rev=3613)),
    (checkouts.TranslatorSvnCheckout(rev=3613),
     checkouts.PreprocessorSvnCheckout(rev='HEAD'),
     checkouts.PlannerSvnCheckout(rev='HEAD')),
               ]

downward_experiments.build_experiment(combinations)
