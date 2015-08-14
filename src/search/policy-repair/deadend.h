#ifndef DEADEND_H
#define DEADEND_H

#include <iostream>
#include <string>
#include <vector>
#include <map>

#include "regression.h"
#include "policy.h"
#include "../successor_generator.h"
#include "../additive_heuristic.h"

void update_deadends(vector< DeadendTuple * > &failed_states);

bool is_deadend(PartialState &state);

bool generalize_deadend(PartialState &state);

bool sample_for_depth1_deadends(const SearchEngine::Plan &plan, PartialState *state);

struct DeadendAwareSuccessorGenerator {
    void generate_applicable_ops(const StateInterface &curr, vector<const Operator *> &ops);
};

#endif
