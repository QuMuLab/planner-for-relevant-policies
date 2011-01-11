# -*- coding: utf-8 -*-

import sys


def read_file(filename):
    try:
        with open(filename) as file:
            return file.read()
    except IOError as e:
        print >> sys.stderr, "error reading %s: %r" % (filename, e)
