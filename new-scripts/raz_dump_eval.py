#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

import dump_eval


def dump(filename=None):
    for heading, attr_dict in dump_eval.parse(filename):
        pairs = ["%s=%s" % pair for pair in sorted(attr_dict.iteritems())]
        assert all("|" not in pair for pair in pairs)
        print "[%s] %s" % (heading, " | ".join(pairs))


if __name__ == "__main__":
    dump()
