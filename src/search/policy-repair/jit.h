#ifndef JIT_H
#define JIT_H

#include <queue>
#include <list>
#include <set>

#include "../globals.h"
#include "../state.h"
#include "../operator.h"
#include "../search_engine.h"
#include "../state_var_t.h"
#include "../option_parser.h"

#include "policy.h"
#include "regression.h"
#include "simulator.h"
#include "deadend.h"

struct UnhandledState {
    State *state;
    int cost;

    UnhandledState(State *s, int c) : state(s), cost(c) {}
    ~UnhandledState() { /*delete state;*/ }
    
    bool operator<(const UnhandledState& other) const { return (cost < other.cost); }
    
    void dump() const;
};

bool perform_jit_repairs(Simulator *sim);

#endif
