#ifndef DEADEND_H
#define DEADEND_H

#include <iostream>
#include <string>
#include <vector>

#include "regression.h"
#include "policy.h"
#include "../successor_generator.h"

void update_deadends(vector<State *> &failed_states);

struct DeadendAwareSuccessorGenerator {
    void generate_applicable_ops(const State &curr, vector<const Operator *> &ops);
};

#endif
