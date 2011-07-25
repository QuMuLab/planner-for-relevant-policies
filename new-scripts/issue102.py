#! /usr/bin/env python
import os
import sys

import checkouts
import downward_experiments


def change_makefile(makefile_path, setting, replacements):
    makefile = open(makefile_path).read()

    for orig, replacement in replacements:
        makefile = makefile.replace(orig, replacement)

    with open(makefile_path, 'w') as f:
        f.write(makefile)


def build_exp():
    """Make sure that the replacements are idempotent."""
    optimizations = ['O0', 'O1', 'O2', 'O3', 'Os']
    settings = [(opt, [('-O3', '-' + opt)]) for opt in optimizations]
    combos = [(checkouts.TranslatorHgCheckout(),
               checkouts.PreprocessorHgCheckout(),
               # If we use "tip" here a new folder is created each time
               checkouts.PlannerHgCheckout(rev='tip', name=opt))
              for opt in optimizations
             ]
    checkouts.checkout(combos)
    # Make adjustments to Makefiles
    for opt, combo in zip(optimizations, combos):
        translator, preprocessor, planner = combo
        planner_name = 'downward-' + opt
        replacements = [('-O3', '-' + opt)]
        makefile_path = os.path.join(planner.exe_dir, 'Makefile')
        print makefile_path
        change_makefile(makefile_path, opt, replacements)

    downward_experiments.build_experiment(combos)


if __name__ == '__main__':
    build_exp()
