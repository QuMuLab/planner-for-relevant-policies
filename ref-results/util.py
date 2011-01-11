# -*- coding: utf-8 -*-

import hashlib
import sys


def hash_id(domain_file, problem_file):
    sha1 = hashlib.sha1()
    for filename in [domain_file, problem_file]:
        with open(filename) as file:
            text = file.read()
        sha1.update(text)
    return sha1.hexdigest()


def read_file(filename):
    try:
        with open(filename) as file:
            return file.read()
    except IOError as e:
        print >> sys.stderr, "error reading %s: %r" % (filename, e)
