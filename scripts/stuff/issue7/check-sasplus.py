#! /usr/bin/env python

## Check that the input pre files are SAS+, i.e., have no derived
## variables or conditional effects.

def check_input(infile):
    def next():
        result = infile.next().rstrip("\n")
        return result
    while next() != "begin_variables":
        pass
    for _ in xrange(int(next())):
        parts = next().split()
        assert len(parts) == 3, parts
        if parts[2] != "-1":
            return "has derived variables"
    assert next() == "end_variables"
    while next() != "end_goal":
        pass
    for _ in xrange(int(next())):
        assert next() == "begin_operator"
        name = next()
        for _ in xrange(int(next())):
            next()
        for _ in xrange(int(next())):
            if next() != "0":
                return "has conditional effects (%s)" % name
            next()
        next()
        assert next() == "end_operator"
    assert next() == "0"
    assert next() == "begin_SG"
    return "is SAS+"
        

if __name__ == "__main__":
    import sys
    for filename in sys.argv[1:]:
        print "%s %s" % (filename, check_input(open(filename)))
