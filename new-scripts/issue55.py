#! /usr/bin/env python

from downward_comparisons import *

branch = 'svn+ssh://downward/branches/translate-andrew/downward/translate'

preprocessor = PreprocessorCheckout()
planner = PlannerCheckout(rev=3842)

combinations = [
    (TranslatorCheckout(repo_url=branch, rev=3827), preprocessor, planner),
    (TranslatorCheckout(repo_url=branch, rev=3829), preprocessor, planner),
    (TranslatorCheckout(repo_url=branch, rev=3840), preprocessor, planner),
    (TranslatorCheckout(rev=4283), preprocessor, planner),
    (TranslatorCheckout(rev=4703), preprocessor, planner),
               ]
               
build_comparison_exp(combinations)
