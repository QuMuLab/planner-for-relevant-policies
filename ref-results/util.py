# -*- coding: utf-8 -*-

import os
import sys


def read_file(filename):
    try:
        with open(filename) as file:
            return file.read()
    except EnvironmentError as e:
        print >> sys.stderr, "error reading %s: %s" % (filename, e)
        sys.exit(1)


def write_file(filename, contents):
    try:
        with open(filename, "w") as file:
            file.write(contents)
    except EnvironmentError as e:
        print >> sys.stderr, "error writing %s: %s" % (filename, e)
        sys.exit(1)


def make_dir(dirname):
    try:
        os.mkdir(dirname)
    except EnvironmentError as e:
        print >> sys.stderr, "error creating directory %s: %s" % (dirname, e)
        sys.exit(1)
