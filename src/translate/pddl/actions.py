from __future__ import print_function

import copy

from . import conditions
from . import effects
from . import pddl_types

class Action(object):
    def __init__(self, name, parameters, num_external_parameters,
                 precondition, effects, cost):
        assert 0 <= num_external_parameters <= len(parameters)
        self.name = name
        self.parameters = parameters
        # num_external_parameters denotes how many of the parameters
        # are "external", i.e., should be part of the grounded action
        # name. Usually all parameters are external, but "invisible"
        # parameters can be created when compiling away existential
        # quantifiers in conditions.
        self.num_external_parameters = num_external_parameters
        self.precondition = precondition
        self.effects = effects
        self.cost = cost
        self.uniquify_variables() # TODO: uniquify variables in cost?
    def __repr__(self):
        return "<Action %r at %#x>" % (self.name, id(self))
    def parse(alist):
        iterator = iter(alist)
        action_tag = next(iterator)
        assert action_tag == ":action"
        name = next(iterator)
        
        # Make sure we bring in nondet actions that are already determinized
        name = 'DETDUP'.join(name.split('detdup'))
        
        parameters_tag_opt = next(iterator)
        if parameters_tag_opt == ":parameters":
            parameters = pddl_types.parse_typed_list(next(iterator),
                                                     only_variables=True)
            precondition_tag_opt = next(iterator)
        else:
            parameters = []
            precondition_tag_opt = parameters_tag_opt
        if precondition_tag_opt == ":precondition":
            precondition_list = next(iterator)
            if not precondition_list:
                # Note that :precondition () is allowed in PDDL.
                precondition = conditions.Conjunction([])
            else:
                precondition = conditions.parse_condition(precondition_list)
                precondition = precondition.simplified()
            effect_tag = next(iterator)
        else:
            precondition = conditions.Conjunction([])
            effect_tag = precondition_tag_opt
        assert effect_tag == ":effect"
        effect_list = next(iterator)
        try:
            cost_eff_pairs = effects.parse_effects(effect_list)
            if len(cost_eff_pairs) > 1:
                ###################
                ## !!!WARNING!!!
                ##   This means that regular non-det actions are not allowed now
                #if 'sense_' == name[:6]:
                # Negate the sensing output
                #  This assumes that we "observe" just a single fluent
                assert 2 == len(cost_eff_pairs)
                
                new_effs1 = filter(lambda x: 'can_observe' not in x.literal.predicate, [eff.copy() for eff in cost_eff_pairs[0][1]])
                new_effs2 = filter(lambda x: 'can_observe' not in x.literal.predicate, [eff.copy() for eff in cost_eff_pairs[1][1]])
                
                for eff in new_effs1 + new_effs2:
                    eff.literal = eff.literal.negate()
                
                cost_eff_pairs[0][1].extend(new_effs2)
                cost_eff_pairs[1][1].extend(new_effs1)
                
                assert '__' not in cost_eff_pairs[0][1][1].literal.predicate
                assert '__' not in cost_eff_pairs[1][1][1].literal.predicate
                
                if isinstance(precondition, conditions.Atom):
                    old_pres = [precondition]
                else:
                    assert isinstance(precondition, conditions.Conjunction)
                    old_pres = list(precondition.parts)
                    print (old_pres)
                
                precondition = conditions.Conjunction(old_pres + [cost_eff_pairs[0][1][1].literal.negate(), cost_eff_pairs[1][1][1].literal.negate()])
                
                cost_eff_pairs = [(cost_eff_pairs[i][0], cost_eff_pairs[i][1], "_DETDUP_%d" % i) for i in range(len(cost_eff_pairs))]
                
            elif False and ('closure_' == name[:8]):
                # If it is a closure action, then we split it up by having
                #  a new action for each conditional effect with the condition
                #  moved into the precondition.
                toReturn = []
                actionMapping = {}
                for cond_eff in cost_eff_pairs[0][1]:
                    
                    if isinstance(cond_eff.condition, conditions.Literal):
                        cond_eff.condition = conditions.Conjunction([cond_eff.condition])
                    if isinstance(precondition, conditions.Literal):
                        precondition = conditions.Conjunction([precondition])
                        
                    assert isinstance(cond_eff.condition, conditions.Conjunction)
                    assert isinstance(precondition, conditions.Conjunction)
                    assert cond_eff.condition.parts > 0
                    
                    if cond_eff.cond_index not in actionMapping:
                        actionMapping[cond_eff.cond_index] = []
                    actionMapping[cond_eff.cond_index].append(cond_eff)
                
                index = 1
                
                for cond_id in actionMapping.keys():
                    
                    new_precondition = conditions.Conjunction(precondition.parts + actionMapping[cond_id][0].condition.parts)
                    
                    #new_eff = conditions.Conjunction(map(lambda x: x.literal, actionMapping[cond_id]))
                    new_eff = map(lambda x: effects.Effect(x.parameters, conditions.Truth(), x.literal), actionMapping[cond_id])
                    
                    toReturn.append(Action("%s_part_%d" % (name, index), parameters, len(parameters), new_precondition, new_eff, cost_eff_pairs[0][0]))
                    
                    #print ("\n\n")
                    #toReturn[-1].dump()
                    
                    index += 1
                    
                #assert False, str(len(cost_eff_pairs[0][1]))
                return toReturn
            else:
                cost_eff_pairs = [(cost_eff_pairs[0][0], cost_eff_pairs[0][1], '')]
        except ValueError as e:
            raise SystemExit("Error in Action %s\nReason: %s." % (name, e))
        for rest in iterator:
            assert False, rest
        return [Action(name + suffix, parameters, len(parameters), precondition, eff, cost) for (cost, eff, suffix) in cost_eff_pairs]
    parse = staticmethod(parse)
    def dump(self):
        print("%s(%s)" % (self.name, ", ".join(map(str, self.parameters))))
        print("Precondition:")
        self.precondition.dump()
        print("Effects:")
        for eff in self.effects:
            eff.dump()
        print("Cost:")
        if(self.cost):
            self.cost.dump()
        else:
            print("  None")
    def uniquify_variables(self):
        self.type_map = dict([(par.name, par.type) for par in self.parameters])
        self.precondition = self.precondition.uniquify_variables(self.type_map)
        for effect in self.effects:
            effect.uniquify_variables(self.type_map)
    def relaxed(self):
        new_effects = []
        for eff in self.effects:
            relaxed_eff = eff.relaxed()
            if relaxed_eff:
                new_effects.append(relaxed_eff)
        return Action(self.name, self.parameters, self.num_external_parameters,
                      self.precondition.relaxed().simplified(),
                      new_effects)
    def untyped(self):
        # We do not actually remove the types from the parameter lists,
        # just additionally incorporate them into the conditions.
        # Maybe not very nice.
        result = copy.copy(self)
        parameter_atoms = [par.to_untyped_strips() for par in self.parameters]
        new_precondition = self.precondition.untyped()
        result.precondition = conditions.Conjunction(parameter_atoms + [new_precondition])
        result.effects = [eff.untyped() for eff in self.effects]
        return result

    def instantiate(self, var_mapping, init_facts, fluent_facts, objects_by_type):
        """Return a PropositionalAction which corresponds to the instantiation of
        this action with the arguments in var_mapping. Only fluent parts of the
        conditions (those in fluent_facts) are included. init_facts are evaluated
        whilte instantiating.
        Precondition and effect conditions must be normalized for this to work.
        Returns None if var_mapping does not correspond to a valid instantiation
        (because it has impossible preconditions or an empty effect list.)"""
        arg_list = [var_mapping[par.name]
                    for par in self.parameters[:self.num_external_parameters]]
        name = "(%s %s)" % (self.name, " ".join(arg_list))

        precondition = []
        try:
            self.precondition.instantiate(var_mapping, init_facts,
                                          fluent_facts, precondition)
        except conditions.Impossible:
            return None
        effects = []
        for eff in self.effects:
            eff.instantiate(var_mapping, init_facts, fluent_facts,
                            objects_by_type, effects)
        # HAZ: We return a propositional action since it may be a failed
        #      outcome of a determinized action.
        if self.cost is None:
            cost = 0
        else:
            cost = int(self.cost.instantiate(var_mapping, init_facts).expression.value)
        return PropositionalAction(name, precondition, effects, cost)
        #if effects:
        #    if self.cost is None:
        #        cost = 0
        #    else:
        #        cost = int(self.cost.instantiate(var_mapping, init_facts).expression.value)
        #    return PropositionalAction(name, precondition, effects, cost)
        #else:
        #    return None

class PropositionalAction:
    def __init__(self, name, precondition, effects, cost):
        self.name = name
        self.precondition = precondition
        self.add_effects = []
        self.del_effects = []
        for condition, effect in effects:
            if not effect.negated:
                self.add_effects.append((condition, effect))
        # Warning: This is O(N^2), could be turned into O(N).
        # But that might actually harm performance, since there are
        # usually few effects.
        # TODO: Measure this in critical domains, then use sets if acceptable.
        for condition, effect in effects:
            if effect.negated and (condition, effect.negate()) not in self.add_effects:
                self.del_effects.append((condition, effect.negate()))
        self.cost = cost
    def __repr__(self):
        return "<PropositionalAction %r at %#x>" % (self.name, id(self))
    def dump(self):
        print(self.name)
        for fact in self.precondition:
            print("PRE: %s" % fact)
        for cond, fact in self.add_effects:
            print("ADD: %s -> %s" % (", ".join(map(str, cond)), fact))
        for cond, fact in self.del_effects:
            print("DEL: %s -> %s" % (", ".join(map(str, cond)), fact))
        print("cost:", self.cost)
