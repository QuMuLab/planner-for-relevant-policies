#! /usr/bin/env python

from downward_experiments import *
import experiments

old_rev = '213202a44ebe'
new_rev = '7bc6764d4116'

old_translator = TranslatorHgCheckout(rev=old_rev)
new_translator = TranslatorHgCheckout(rev=new_rev)
preprocessor = PreprocessorHgCheckout(rev=old_rev)
planner = PlannerHgCheckout(rev=old_rev)


combinations = [
    (old_translator, preprocessor, planner),
    (new_translator, preprocessor, planner),
               ]
               
build_experiment(combinations)
