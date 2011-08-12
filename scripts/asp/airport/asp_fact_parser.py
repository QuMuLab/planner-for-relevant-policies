# -*- coding: utf-8 -*-

def transform_arg(arg):
    return arg
    #if arg.isdigit():
    #    return arg
    #else:
    #    return "o" + arg
    
def remove_comments(text):
    string_aux = ""
    for line in text.split('\n'):
        if line.strip() and line[0] != "%":
            string_aux += line + '\n'
    return string_aux[:-1]

class AspInstance(object):
    def __init__(self, facts):
        self.facts = facts

    def __getitem__(self, predicate):
        return FactCollection([fact for fact in self.facts
                               if fact.predicate == predicate])

class FactCollection(object):
    def __init__(self, facts):
        self.facts = facts

    def objects(self):
        result = set()
        for fact in self.facts:
            result.update(fact.args)
        return result

    def tuples(self):
        return [fact.args for fact in self.facts]


class Fact(object):
    def __init__(self, predicate, args):
        self.predicate = predicate
        self.args = [transform_arg(arg) for arg in args]

    def __repr__(self):
        return "(%s %s)" % (self.predicate, " ".join(self.args))


def parse(filename):
    text = open(filename).read().strip()
    text = remove_comments(text)
    facts = []
    if text:
        assert text.endswith("."), text
        text = text[:-1]
        for fact_string in text.split("."):
            fact_string = fact_string.strip()
            predicate, match, args = fact_string.partition("(")
            assert match
            assert args.endswith(")")
            args = args[:-1]
            args = args.split(",")
            predicate = predicate.strip()
            args = [arg.strip() for arg in args]
            facts.append(Fact(predicate, args))
    return AspInstance(facts)
