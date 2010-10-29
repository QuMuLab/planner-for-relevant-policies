#! /usr/bin/env python

from downward_comparisons import *

combinations = [
    (TranslatorSvnCheckout(rev=3613), PreprocessorSvnCheckout(), PlannerSvnCheckout(rev=3612)),
    (TranslatorSvnCheckout(rev=3613), PreprocessorSvnCheckout(), PlannerSvnCheckout(rev=3613)),
    (TranslatorSvnCheckout(rev=3613), PreprocessorSvnCheckout(), PlannerSvnCheckout(rev='HEAD')),
               ]
               
build_experiment(combinations)
