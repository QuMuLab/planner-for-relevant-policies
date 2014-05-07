#ifndef DEADEND_H
#define DEADEND_H

#include <iostream>
#include <string>
#include <vector>

#include "regression.h"
#include "policy.h"
#include "../successor_generator.h"
#include "../additive_heuristic.h"

void update_deadends(vector<PartialState *> &failed_states);

bool is_deadend(PartialState &state);

void generalize_deadend(PartialState &state);

struct DeadendAwareSuccessorGenerator {
    void generate_applicable_ops(const State &curr, vector<const Operator *> &ops);
};

#endif
