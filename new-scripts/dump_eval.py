#! /usr/bin/env python2.6
# -*- coding: utf-8 -*-

import os.path
import re
import sys
import tools


def _get_filename_from_command_line():
    args = sys.argv[1:]
    if len(args) != 1:
        sys.exit("usage: %s EVAL_DIR" % os.path.basename(sys.argv[0]))
    return os.path.join(args[0], "properties")


def parse(filename=None):
    """Parse a 'properties' file of an evaluation directory,
    validate it and return it as a list of (str, dict) pairs,
    where the str is the 'title' of each property section.

    Validation tests that no unexpected characters are contained in
    the headings, keys or dicts. (See code for details.)

    If no filename is specified, use sys.argv to determine it."""
    if filename is None:
        filename = _get_filename_from_command_line()

    # Allowed identifiers are like C++ identifiers except that
    # also permit dots and dashes after the first character.
    re_identifier = re.compile(r"^[a-zA-Z_][-.\w]*$")
    def is_legal_identifier(text):
        return bool(re_identifier.match(text))

    # Values may not be empty and allowed characters are limited to:
    # * Letters, digits and underscores ('a'-'z', 'A'-'Z', '0'-'9', '_')
    # * Space characters: ' '
    # * Characters from this string: "-=/()[]{}'.,"
    re_value = re.compile(r"^[\w \-=/()\[\]{}'.,]+$")
    def is_legal_value(text):
        return bool(re_value.match(text))

    properties = tools.Properties(filename, file_error=True)
    result = []
    for heading, section in properties.iteritems():
        assert is_legal_identifier(heading), heading
        items = sorted(section.iteritems())
        for key, attr in sorted(section.iteritems()):
            assert is_legal_identifier(key), (heading, key, attr)
            attr_text = str(attr)
            assert is_legal_value(attr_text), (heading, key, attr)
        result.append((heading, dict(section)))
    return result


def dump(filename=None):
    for heading, attr_dict in parse(filename):
        print "[%s]" % heading
        for key, value in sorted(attr_dict.iteritems()):
            print "%s = %s" % (key, value)
        print

if __name__ == "__main__":
    dump()
