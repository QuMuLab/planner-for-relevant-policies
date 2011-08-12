#! /usr/bin/env python
import os

import checkouts
from checkouts import Translator, Preprocessor, Planner
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
    # We use "tip" here to have a new folder be created each time
    combos = [(Translator(), Preprocessor(), Planner(rev='tip', dest=opt))
              for opt in optimizations]
    checkouts.checkout(combos)
    # Make adjustments to Makefiles
    for opt, combo in zip(optimizations, combos):
        translator, preprocessor, planner = combo
        replacements = [('-O3', '-' + opt)]
        makefile_path = os.path.join(planner.bin_dir, 'Makefile')
        change_makefile(makefile_path, opt, replacements)

    downward_experiments.build_experiment(combos)


if __name__ == '__main__':
    build_exp()
