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


def build_makefile_exp(settings):
    """Make sure that the replacements are idempotent."""
    # We use "tip" here to have a new folder be created each time
    combos = [(Translator(), Preprocessor(), Planner(rev='tip', dest=name))
              for name, replacements in settings]
    checkouts.checkout(combos)
    # Make adjustments to Makefiles
    for (name, replacements), combo in zip(settings, combos):
        translator, preprocessor, planner = combo
        makefile_path = os.path.join(planner.bin_dir, 'Makefile')
        change_makefile(makefile_path, opt, replacements)

    downward_experiments.build_experiment(combos)


if __name__ == '__main__':
    settings = [(opt, [('-O3', '-' + opt)])
                for opt in 'O0 O1 O2 O3 Os'.split()]
    settings = [
        ('nopoint_noassert', []),
        ('point_noassert', [('-fomit-frame-pointer', '')]),
        ('nopoint_assert', [('-DNDEBUG', '')]),
        ('point_assert', [('-fomit-frame-pointer', ''), ('-DNDEBUG', '')]),]
    build_makefile_exp(settings)
