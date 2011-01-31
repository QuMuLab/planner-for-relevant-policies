#! /usr/bin/env python

from downward_experiments import *

old_rev = '213202a44ebe'
new_rev = '4dc3a033242a'

old_translator = TranslatorHgCheckout(rev=old_rev)
new_translator = TranslatorHgCheckout(rev=new_rev)
preprocessor = PreprocessorHgCheckout(rev=old_rev)
planner = PlannerHgCheckout(rev=old_rev)


combinations = [
    (old_translator, preprocessor, planner),
    (new_translator, preprocessor, planner),
               ]

build_experiment(combinations)
