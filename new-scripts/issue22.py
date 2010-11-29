#! /usr/bin/env python

from downward_experiments import *

translator1 = TranslatorHgCheckout(rev=750)
translator2 = TranslatorHgCheckout(rev='WORK')
preprocessor = PreprocessorHgCheckout()

combinations = [
    (translator1, preprocessor),
    (translator2, preprocessor),
               ]

if __name__ == '__main__':
    build_preprocess_exp(combinations)
