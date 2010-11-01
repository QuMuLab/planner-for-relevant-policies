#! /usr/bin/env python

from downward_experiments import *

old_rev = 'a71e8f733599'
new_rev = '952811b6757e'

repo = '../'


combinations = [
    (TranslatorHgCheckout(repo=repo, rev=old_rev), PreprocessorHgCheckout(repo=repo, rev=old_rev), PlannerHgCheckout(repo=repo, rev=old_rev)),
    (TranslatorHgCheckout(repo=repo, rev=new_rev), PreprocessorHgCheckout(repo=repo, rev=old_rev), PlannerHgCheckout(repo=repo, rev=old_rev)),
               ]
               
build_experiment(combinations)
