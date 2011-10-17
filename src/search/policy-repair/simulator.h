#ifndef SIMULATOR_H
#define SIMULATOR_H

#include <cstdlib>
#include <iostream>
#include <string>
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
    
    void execute_action(const Operator *op);
    
    bool verbose;
    
public:
    Simulator(SearchEngine *eng, int argc, const char **argv, bool verb = true);
    
    void run();
    void replan();
    
    void set_state(State * s) { current_state = new State(*s); }
    SearchEngine * get_engine() { return engine; }
    
    bool found_solution;
    
    void dump();
    
};

#endif
