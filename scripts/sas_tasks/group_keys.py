#! /usr/bin/env python2.5
# -*- coding: utf-8 -*-

import re

from myiterators import EolStripIterator, LookaheadIterator


class GroupKey(object):
    def __init__(self, groups):
        self.groups = groups
        self.groupdict = dict((group.varname, group) for group in groups)

    def __iter__(self):
        return iter(self.groups)

    def __getitem__(self, varname):
        return self.groupdict[varname]

    def dump(self, out=None):
        for group in self.groups:
            group.dump(out)


class Group(object):
    def __init__(self, varname, values):
        self.varname = varname
        self.values = values

    def __getitem__(self, no):
        return self.values[no]

    def dump(self, out=None):
        print >> out, "%s:" % self.varname
        for no, value in enumerate(self.values):
            print >> out, "%3d: %s" % (no, value)


def read(filename):
    iterator = EolStripIterator(open(filename))
    return parse(iterator)

def parse(lines):
    iter = LookaheadIterator(lines)
    groups = []
    while iter.peek() is not None:
        groups.append(parse_group(iter))
    return GroupKey(groups)

def parse_group(iter):
    varname_re = re.compile(r"(.+):$")
    value_re = re.compile(r"\s*(\d+): (?:Atom )?(.+|<none of those>)$")

    var_line = iter.next()
    match = varname_re.match(var_line)
    if not match:
        raise ValueError(var_line)
    varname = match.group(1)
    values = []
    while iter.peek() is not None and value_re.match(iter.peek()):
        match = value_re.match(iter.next())
        value_no = int(match.group(1))
        value_name = match.group(2)
        if value_no != len(values):
            raise ValueError(value_line)
        values.append(value_name)
    return Group(varname, values)


if __name__ == "__main__":
    import sys
    for filename in sys.argv[1:]:
        group_key = read(filename)
        group_key.dump()

