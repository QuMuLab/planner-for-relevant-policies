from __future__ import print_function

from fractions import Fraction
import math

from . import conditions
from . import pddl_types
from . import f_expression

def cartesian_product(*sequences):
    # TODO: Also exists in tools.py outside the pddl package (defined slightly
    #       differently). Not good. Need proper import paths.
    if not sequences:
        yield ()
    else:
        for tup in cartesian_product(*sequences[1:]):
            for item in sequences[0]:
                yield (item,) + tup

def get_inferred_cost(prob):
    # This method infers a cost from a given probability
    # These costs will help heuristic search in the planner
    #return 2 + int((1.3 + (math.log10(1 - min(0.95, prob))))*100)
    scaling_factor = 300.0
    return int((-scaling_factor) * math.log10(min(0.95, max(0.05, prob))))

def parse_effects(alist):
    """Parse a PDDL effect (any combination of simple, conjunctive, conditional, and universal)."""
    try:
        tmp_effects = parse_effect(alist)
    except Exception as e:
        print("Error in parsing %s" % (str(alist)))
        raise e
    normalized = [tmp_effect.normalize() for tmp_effect in tmp_effects]
    cost_rest_eff = [norm.extract_cost() for norm in normalized]
    cost_eff_prob_triples = []
    for (cost_eff, rest_effect) in cost_rest_eff:
        res = []
        add_effect(rest_effect, res)
        prob = get_probability(rest_effect)
        if cost_eff:
            cost_eff_prob_triples.append((cost_eff.effect, res, prob))
        else:
            # Here we can use the probability to assign a cost to help heuristics
            approximated_cost = get_inferred_cost(prob)
            cost_eff_prob_triples.append((approximated_cost, res, prob))
    return cost_eff_prob_triples

def add_effect(tmp_effect, result):
    """tmp_effect has the following structure:
       [ConjunctiveEffect] {[UniversalEffect] [ConditionalEffect] SimpleEffect}."""

    if isinstance(tmp_effect, ConjunctiveEffect):
        for effect in tmp_effect.effects:
            add_effect(effect, result)
        return
    else:
        parameters = []
        condition = conditions.Truth()
        if isinstance(tmp_effect, UniversalEffect):
            parameters = tmp_effect.parameters
            if isinstance(tmp_effect.effect, ConditionalEffect):
                condition = tmp_effect.effect.condition
                assert isinstance(tmp_effect.effect.effect, SimpleEffect)
                effect = tmp_effect.effect.effect.effect
            else:
                assert isinstance(tmp_effect.effect, SimpleEffect)
                effect = tmp_effect.effect.effect
        elif isinstance(tmp_effect, ConditionalEffect):
            condition = tmp_effect.condition
            assert isinstance(tmp_effect.effect, SimpleEffect)
            effect = tmp_effect.effect.effect
        else:
            assert isinstance(tmp_effect, SimpleEffect)
            effect = tmp_effect.effect
        if (effect is None):
            # Nothing to add
            return
        assert isinstance(effect, conditions.Literal)
        
        # Check for contradictory effects if the effect is non-null
        condition = condition.simplified()
        new_effect = Effect(parameters, condition, effect)
        contradiction = Effect(parameters, condition, effect.negate())
        if not contradiction in result:
            result.append(new_effect)
        else:
            # We use add-after-delete semantics, keep positive effect
            if isinstance(contradiction.literal, conditions.NegatedAtom):
                result.remove(contradiction)
                result.append(new_effect)

def get_probability(tmp_effect):
    """Finds the resulting probability of multiplying each conditional probability in
       tmp_effect. The structure of tmp_effect is the same as above:
       [ConjunctiveEffect] {[UniversalEffect] [ConditionalEffect] SimpleEffect}."""
    if isinstance(tmp_effect, ConjunctiveEffect):
        base_probability = tmp_effect.probability
        for effect in tmp_effect.effects:
            base_probability *= get_probability(effect)
        return base_probability
    else:
        return tmp_effect.probability


def parse_effect(alist):
    tag = alist[0]
    if tag == "and":
        return [ConjunctiveEffect(conjuncts) for conjuncts in cartesian_product(*[parse_effect(eff) for eff in alist[1:]])]
    elif tag == "forall":
        assert len(alist) == 3
        parameters = pddl_types.parse_typed_list(alist[1])
        effects = parse_effect(alist[2])
        assert 1 == len(effects), "Error: Cannot embed non-determinism inside of a forall (for now)."
        return [UniversalEffect(parameters, effect) for effect in effects]
    elif tag == "when":
        assert len(alist) == 3
        condition = conditions.parse_condition(alist[1])
        effects = parse_effect(alist[2])
        return [ConditionalEffect(condition, effect) for effect in effects]
    elif tag == "increase":
        assert len(alist) == 3
        assert alist[1] == ['total-cost']
        assignment = f_expression.parse_assignment(alist)
        return [CostEffect(assignment)]
    elif tag == "oneof":
        # Note: Non-determinism needs an extra mechanism to work with probability
        #       The easiest extension is below: Just uniformly weight the outcomes
        options = []
        prob = Fraction(1, len(alist)-1)
        for outcome in alist[1:]:
            for eff in parse_effect(outcome):
                eff.probability *= prob
                options.append(eff)
        return options
    elif tag == "probabilistic":
        # Generate effects for each outcome and then set their probability appropriately
        assert (len(alist)-1) % 2 == 0, "Each probabilistic outcome must have an associated probability"
        outcome_pairs = [(alist[i], alist[i+1]) for i in range(1, len(alist), 2)]

        remaining_probability = Fraction(1)
        outcomes = []
        for pair in outcome_pairs:
            effects = parse_effect(pair[1])
            for eff in effects:
                # Apply the base probability in the pair to this individual effect
                eff.probability *= Fraction(pair[0]).limit_denominator()
                remaining_probability -= eff.probability
                outcomes.append(eff)
        remaining_probability = remaining_probability.limit_denominator()
        if (remaining_probability > 0):
            remaining_eff = SimpleEffect(None)
            remaining_eff.probability = remaining_probability
            outcomes.append(remaining_eff)
        return outcomes
    else:
        return [SimpleEffect(conditions.parse_literal(alist))]


class Effect(object):
    def __init__(self, parameters, condition, literal):
        self.parameters = parameters
        self.condition = condition
        self.literal = literal
    def __eq__(self, other):
        return (self.__class__ is other.__class__ and
                self.parameters == other.parameters and
                self.condition == other.condition and
                self.literal == other.literal)
    def dump(self):
        indent = "  "
        if self.parameters:
            print("%sforall %s" % (indent, ", ".join(map(str, self.parameters))))
            indent += "  "
        if self.condition != conditions.Truth():
            print("%sif" % indent)
            self.condition.dump(indent + "  ")
            print("%sthen" % indent)
            indent += "  "
        print("%s%s" % (indent, self.literal))
    def copy(self):
        return Effect(self.parameters, self.condition, self.literal)
    def uniquify_variables(self, type_map):
        renamings = {}
        self.parameters = [par.uniquify_name(type_map, renamings)
                           for par in self.parameters]
        self.condition = self.condition.uniquify_variables(type_map, renamings)
        self.literal = self.literal.rename_variables(renamings)
    def instantiate(self, var_mapping, init_facts, fluent_facts,
                    objects_by_type, result):
        if self.parameters:
            var_mapping = var_mapping.copy() # Will modify this.
            object_lists = [objects_by_type.get(par.type, [])
                            for par in self.parameters]
            for object_tuple in cartesian_product(*object_lists):
                for (par, obj) in zip(self.parameters, object_tuple):
                    var_mapping[par.name] = obj
                self._instantiate(var_mapping, init_facts, fluent_facts, result)
        else:
            self._instantiate(var_mapping, init_facts, fluent_facts, result)
    def _instantiate(self, var_mapping, init_facts, fluent_facts, result):
        condition = []
        try:
            self.condition.instantiate(var_mapping, init_facts, fluent_facts, condition)
        except conditions.Impossible:
            return
        effects = []
        self.literal.instantiate(var_mapping, init_facts, fluent_facts, effects)
        assert len(effects) <= 1
        if effects:
            result.append((condition, effects[0]))
    def relaxed(self):
        if self.literal.negated:
            return None
        else:
            return Effect(self.parameters, self.condition.relaxed(), self.literal)
    def simplified(self):
        return Effect(self.parameters, self.condition.simplified(), self.literal)


class ConditionalEffect(object):
    def __init__(self, condition, effect, probability=1):
        if isinstance(effect, ConditionalEffect):
            self.condition = conditions.Conjunction([condition, effect.condition])
            self.effect = effect.effect
            probability = Fraction(probability).limit_denominator() * effect.probability
        else:
            self.condition = condition
            self.effect = effect
        self.probability = Fraction(probability).limit_denominator()
    def dump(self, indent="  "):
        if (self.probability < 1):
            print ("%s%.2f%% chance of" % (indent, float(self.probability)*100))
            indent += "  "
        print("%sif" % (indent))
        self.condition.dump(indent + "  ")
        print("%sthen" % (indent))
        self.effect.dump(indent + "  ")
    def normalize(self):
        norm_effect = self.effect.normalize()
        if isinstance(norm_effect, ConjunctiveEffect):
            new_effects = []
            for effect in norm_effect.effects:
                assert isinstance(effect, SimpleEffect) or isinstance(effect, ConditionalEffect)
                new_effects.append(ConditionalEffect(self.condition, effect))
            return ConjunctiveEffect(new_effects, self.probability)
        elif isinstance(norm_effect, UniversalEffect):
            child = norm_effect.effect
            cond_effect = ConditionalEffect(self.condition, child, self.probability)
            return UniversalEffect(norm_effect.parameters, cond_effect)
        else:
            return ConditionalEffect(self.condition, norm_effect, self.probability)
    def extract_cost(self):
        return None, self

class UniversalEffect(object):
    def __init__(self, parameters, effect, probability=1):
        if isinstance(effect, UniversalEffect):
            self.parameters = parameters + effect.parameters
            self.effect = effect.effect
            probability = Fraction(probability).limit_denominator() * effect.probability
        else:
            self.parameters = parameters
            self.effect = effect
        self.probability = Fraction(probability).limit_denominator()
    def dump(self, indent="  "):
        if (self.probability < 1):
            print ("%s%.2f%% chance of" % (indent, float(self.probability)*100))
            indent += "  "
        print("%sforall %s" % (indent, ", ".join(map(str, self.parameters))))
        self.effect.dump(indent + "  ")
    def normalize(self):
        norm_effect = self.effect.normalize()
        if isinstance(norm_effect, ConjunctiveEffect):
            new_effects = []
            for effect in norm_effect.effects:
                assert isinstance(effect, SimpleEffect) or isinstance(effect, ConditionalEffect)\
                       or isinstance(effect, UniversalEffect)
                new_effects.append(UniversalEffect(self.parameters, effect, self.probability))
            return ConjunctiveEffect(new_effects)
        else:
            return UniversalEffect(self.parameters, norm_effect, self.probability)
    def extract_cost(self):
        return None, self

class ConjunctiveEffect(object):
    def __init__(self, effects, probability=1):
        flattened_effects = []
        for effect in effects:
            if isinstance(effect, ConjunctiveEffect):
                flattened_effects += effect.effects
                probability = Fraction(probability).limit_denominator() * effect.probability
            elif (effect.effect != None):
                flattened_effects.append(effect)
            else:
                # This is a None effect - just absorb its probability
                probability = Fraction(probability).limit_denominator() * effect.probability
        self.effects = flattened_effects
        self.probability = Fraction(probability).limit_denominator()
    def dump(self, indent="  "):
        if (self.probability < 1):
            print ("%s%.2f%% chance of" % (indent, float(self.probability)*100))
            indent += "  "
        print("%sand" % indent)
        for eff in self.effects:
            eff.dump(indent + "  ")
    def normalize(self):
        new_effects = []
        for effect in self.effects:
            new_effects.append(effect.normalize())
        return ConjunctiveEffect(new_effects, self.probability)
    def extract_cost(self):
        new_effects = []
        cost_effect = None
        for effect in self.effects:
            if isinstance(effect, CostEffect):
                cost_effect = effect
            else:
                new_effects.append(effect)
        return cost_effect, ConjunctiveEffect(new_effects, self.probability)

class SimpleEffect(object):
    def __init__(self, effect, probability=1):
        self.effect = effect # Note that a None effect may be passed
        self.probability = Fraction(probability).limit_denominator()
    def dump(self, indent="  "):
        if (self.probability < 1):
            print ("%s%.2f%% chance of" % (indent, float(self.probability)*100))
            indent += "  "
        print("%s%s" % (indent, self.effect))
    def normalize(self):
        return self
    def extract_cost(self):
        return None, self

class CostEffect(object):
    def __init__(self, effect, probability=1):
        self.effect = effect
        self.probability = Fraction(probability).limit_denominator()
    def dump(self, indent="  "):
        if (self.probability < 1):
            print ("%s%.2f%% chance of" % (indent, float(self.probability)*100))
            indent += "  "
        print("%s%s" % (indent, self.effect))
    def normalize(self):
        return self
    def extract_cost(self):
        return self, None # this would only happen if
    #an action has no effect apart from the cost effect
