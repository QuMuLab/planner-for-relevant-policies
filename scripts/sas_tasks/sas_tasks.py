#! /usr/bin/env python2.5
# -*- coding: utf-8 -*-

import itertools
import os.path

from myiterators import EolStripIterator, LookaheadIterator
import group_keys


class SasTask(object):
    def __init__(self, name, variables, initial_state, goals, operators, axioms):
        self.name = name
        self.variables = variables
        self.initial_state = initial_state
        self.goals = goals
        self.operators = operators
        self.axioms = axioms

    def dump(self):
        print "Task %s" % self.name
        print "Variables:"
        for var in self.variables:
            print "  %s" % var
        print
        print "Init:"
        for prop in self.initial_state:
            print "  %s" % prop
        print
        print "Goals:"
        for prop in self.goals:
            print "  %s" % prop
        print
        for op in self.operators:
            op.dump()
            print
        for axiom in self.axioms:
            axiom.dump()
            print


class Variable(object):
    def __init__(self, name, values, axiom_layer):
        self.name = name
        self.propositions = [Proposition(self, value) for value in values]
        self.axiom_layer = axiom_layer

    @property
    def range(self):
        return len(self.propositions)

    @property
    def is_axiom(self):
        return self.axiom_layer != -1

    def __str__(self):
        values = map(str, self.propositions)
        if self.is_axiom:
            layer_info = " [layer %d]" % self.axiom_layer
        else:
            layer_info = ""
        return "%s in {%s}%s" % (self.name, ", ".join(values), layer_info)


class Proposition(object):
    def __init__(self, var, name):
        self.var = var
        self.name = name

    def __repr__(self):
        return self.name


class Operator(object):
    def __init__(self, name, precond, effects):
        # Note that we compile away "prevail conditions" and
        # "preconditions" into a single set of "preconditions".
        self.name = name
        self.precond = precond
        self.effects = effects

    def dump(self):
        print self.name
        for precond in self.precond:
            print "  PRE: %s" % precond
        for conds, effect in self.effects:
            if conds:
                cond_spec = ", ".join(map(str, conds))
            else:
                cond_spec = ""
            print "  EFF: %s%s" % (cond_spec, effect)


class Axiom(object):
    def __init__(self, cond, derive):
        self.cond = cond
        self.derive = derive

    def dump(self):
        for cond in self.cond:
            print "  IFCOND: %s" % cond
        print "  DERIVE: %s" % self.derive


class SymbolTable(object):
    def __init__(self, variables):
        self.variables = variables

    def __getitem__(self, (var_no, value_no)):
        # Don't allow indexing with negative indices.
        assert 0 <= var_no < len(self.variables)
        var = self.variables[var_no]
        assert 0 <= value_no < var.range
        return var.propositions[value_no]
        

# factory functions
def read(filename, key_filename):
    stem = os.path.splitext(filename)[0]
    key = group_keys.read(key_filename)
    iterator = EolStripIterator(open(filename))
    return parse(os.path.basename(stem), iterator, key)


def parse(name, lines, key):
    iter = LookaheadIterator(lines)
    variables = parse_variables(iter, key)
    symtab = SymbolTable(variables)
    init = parse_initial_state(iter, len(variables), symtab)
    goals = parse_goals(iter, symtab)
    operators = parse_operators(iter, symtab)
    axioms = parse_axioms(iter, symtab)
    if iter.peek() is not None:
        raise ValueError(iter.next())
    assert_layering_rule(init, axioms)
    return SasTask(name, variables, init, goals, operators, axioms)


# generic helper functions for parsing
def match(iterator, item_to_match):
    item = iterator.next()
    if item != item_to_match:
        raise ValueError("got %r, expected %r" % (item, item_to_match))

def match_int(iterator):
    return int(iterator.next())

def match_ints(iterator):
    return map(int, iterator.next().split())

def match_tuple(iterator, *types):
    parts = iterator.next().split()
    return tuple(type(part) for type, part in zip(types, parts))

def match_counted_tuples(iterator, *types):
    num_entries = match_int(iterator)
    return [match_tuple(iterator, *types) for _ in xrange(num_entries)]

def assert_vars_unique(propositions):
    variables = set(prop.var for prop in propositions)
    assert len(variables) == len(propositions)
    

# functions that do the legwork of parsing
def parse_variables(iter, key):
    match(iter, "begin_variables")
    data = match_counted_tuples(iter, str, int, int)
    match(iter, "end_variables")
    result = []
    for var_name, var_range, layer in data:
        assert layer == -1 or layer >= 0
        if layer != -1:
            assert var_range == 2
        assert var_range >= 2
        values = key[var_name].values
        assert var_range == len(values)
        assert len(values) == len(set(values))
        result.append(Variable(var_name, values, layer))
    varnames = set(var.name for var in result)
    assert len(result) == len(varnames)
    return result

def parse_initial_state(iter, num_variables, symtab):
    match(iter, "begin_state")
    value_nos = [match_int(iter) for _ in xrange(num_variables)]
    result = [symtab[var_no, value_no]
              for var_no, value_no in enumerate(value_nos)]
    match(iter, "end_state")
    return result

def parse_goals(iter, symtab):
    match(iter, "begin_goal")
    goals = [symtab[var_no, value_no]
             for var_no, value_no in match_counted_tuples(iter, int, int)]
    match(iter, "end_goal")
    assert_vars_unique(goals)
    return goals

def parse_operators(iter, symtab):
    operator_count = match_int(iter)
    return [parse_operator(iter, symtab)
            for _ in xrange(operator_count)]

def parse_operator(iter, symtab):
    match(iter, "begin_operator")
    name = iter.next()
    precond = [symtab[var_no, value_no]
               for var_no, value_no in match_counted_tuples(iter, int, int)]
    effects = []
    for _ in xrange(match_int(iter)):
        parts = match_ints(iter)
        assert len(parts) >= 4
        cond_no = parts[0]
        var_no, pre_no, post_no = parts[-3:]
        if pre_no != -1:
            precond.append(symtab[var_no, pre_no])
        remaining_parts = parts[1:-3]
        assert len(remaining_parts) == 2 * cond_no
        effconds = []
        for ec_var_no, ec_value_no in zip(effconds[::2], effconds[1::2]):
            effconds.append(symtab[ec_var_no, ec_value_no])
        assert_vars_unique(effconds)
        effect_prop = symtab[var_no, post_no]
        assert not effect_prop.var.is_axiom
        effects.append((effconds, effect_prop))
    match(iter, "end_operator")
    assert_vars_unique(precond)
    return Operator(name, precond, effects)

def parse_axioms(iter, symtab):
    axiom_count = match_int(iter)
    return [parse_axiom(iter, symtab)
            for _ in xrange(axiom_count)]

def parse_axiom(iter, symtab):
    # TODO: Check layering condition.
    match(iter, "begin_rule")
    cond = [symtab[var_no, value_no]
            for var_no, value_no in match_counted_tuples(iter, int, int)]
    derive_var_no, derive_pre_no, derive_post_no = match_tuple(iter, int, int, int)
    match(iter, "end_rule")
    assert derive_pre_no != -1
    if derive_pre_no != -1:
        cond.append(symtab[derive_var_no, derive_pre_no])
    derive = symtab[derive_var_no, derive_post_no]
    assert derive.var.is_axiom
    return Axiom(cond, derive)

def assert_layering_rule(init, axioms):
    init_set = set(init)
    for axiom in axioms:
        assert_layering_rule_axiom(init_set, axiom)

def assert_layering_rule_axiom(init_set, axiom):
    for prop in axiom.cond:
        assert prop is not axiom.derive
        if not prop.var.is_axiom or prop.var is axiom.derive.var:
            continue
        derive_layer = axiom.derive.var.axiom_layer
        prop_layer = prop.var.axiom_layer
        assert derive_layer >= prop_layer
        if derive_layer == prop_layer:
            is_fake_axiom = axiom.derive in init_set
            assert (prop in init_set) == is_fake_axiom

if __name__ == "__main__":
    import sys
    task = read(sys.argv[1], sys.argv[2])
    # task.dump()
