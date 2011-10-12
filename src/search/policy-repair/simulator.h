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

#include "policy.h"
#include "regression.h"

class Simulator {
    Policy *policy;
    State *current_state;
    SearchEngine *engine;
    
    int successful_states;
    int failed_states;
    
    void execute_action(const Operator *op);
    void replan();
    
public:
    Simulator(Policy *pol, SearchEngine *eng);
    
    void run();
    
    void dump();
    
};

#endif
