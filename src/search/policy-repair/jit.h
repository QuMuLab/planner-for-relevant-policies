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

struct UnhandledState {
    PartialState *state;
    int cost;

    UnhandledState(PartialState *s, int c) : state(s), cost(c) {}
    ~UnhandledState() { /*delete state;*/ }
    
    bool operator<(const UnhandledState& other) const { return (cost < other.cost); }
    
    void dump() const;
};

bool perform_jit_repairs(Simulator *sim);

#endif
