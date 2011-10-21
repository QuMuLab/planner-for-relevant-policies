#ifndef SIMULATOR_H
#define SIMULATOR_H

#include <cstdlib>
#include <iostream>
#include <string>
#include <queue>
#include <list>

#include "../globals.h"
#include "../state.h"
#include "../operator.h"
#include "../search_engine.h"
#include "../state_var_t.h"
#include "../rng.h"

#include "policy.h"
#include "regression.h"

class Simulator {
    State *current_state;
    
    SearchEngine *engine;
    int argc;
    const char **argv;
    
    int successful_states;
    int failed_states;
    
    bool execute_action(const Operator *op);
    
    bool verbose;
    bool succeeded;
    
public:
    Simulator(SearchEngine *eng, int argc, const char **argv, bool verb = true);
    
    void run();
    void run_ffreplan(queue<const Operator *> &plan);
    bool replan();
    
    void set_state(State * s) { current_state = new State(*s); }
    SearchEngine * get_engine() { return engine; }
    
    bool found_solution;
    
    void dump();
    
};

#endif
