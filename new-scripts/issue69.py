#! /usr/bin/env python

from downward_comparisons import *

combinations = [
    (TranslatorCheckout(), PreprocessorCheckout(), PlannerCheckout(rev=3612)),
    (TranslatorCheckout(), PreprocessorCheckout(), PlannerCheckout(rev=3613)),
    (TranslatorCheckout(), PreprocessorCheckout(), PlannerCheckout(rev='HEAD')),
               ]
               
build_comparison_exp(combinations)
