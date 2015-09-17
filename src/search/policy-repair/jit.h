#ifndef JIT_H
#define JIT_H

#include <stack>
#include <list>
#include <set>

#include "../globals.h"
#include "../operator.h"
#include "../search_engine.h"
#include "../option_parser.h"

#include "policy.h"
#include "regression.h"
#include "simulator.h"
#include "deadend.h"
#include "partial_state.h"

class Simulator;

struct UnhandledState {
    PartialState *state;
    int cost;

    UnhandledState(PartialState *s, int c) : state(s), cost(c) {}
    ~UnhandledState() { /*delete state;*/ }

    bool operator<(const UnhandledState& other) const { return (cost < other.cost); }

    void dump() const;
};

bool perform_jit_repairs(Simulator *sim);

struct SCNode {
    PartialState * full_state;
    PartialState * expected_state;
    PartialState * previous_state;
    RegressionStep * prev_regstep;
    const Operator * prev_op;
    SCNode(PartialState * fs, PartialState * es, PartialState * ps, RegressionStep * pr, const Operator * op) :
       full_state(fs), expected_state(es), previous_state(ps), prev_regstep(pr), prev_op(op) {}
};

#endif
