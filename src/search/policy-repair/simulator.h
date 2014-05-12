#ifndef SIMULATOR_H
#define SIMULATOR_H

#include <iostream>
#include <cstdlib>
#include <string>
#include <vector>
#include <cmath>
#include <queue>
#include <list>

#include "../globals.h"
#include "../state.h"
#include "../operator.h"
#include "../search_engine.h"
#include "../rng.h"

#include "policy.h"
#include "regression.h"
#include "partial_state.h"

using namespace std;

class Simulator {
    PartialState *current_state;
    PartialState *current_goal;
    
    SearchEngine *engine;
    int argc;
    const char **argv;
    
    int successful_states;
    int failed_states;
    
    int record_succeeded;
    int record_depth_limit;
    vector<int> record_successful_states;
    vector<int> record_failed_states;
    vector<int> record_total_states;
    
    bool execute_action(const Operator *op);
    
    bool verbose;
    bool found_solution;
    
public:
    Simulator(SearchEngine *eng, int argc, const char **argv, bool verb = true);
    Simulator(bool verb = true);
    
    void run();
    void run_once(bool stop_on_failure = false, Policy *pol = g_policy);
    bool replan();
    
    void set_state(PartialState * s) { current_state = new PartialState(*s); }
    void set_goal(PartialState * s) { current_goal = new PartialState(*s); }
    
    void record_stats();
    void reset_goal();
    
    SearchEngine * get_engine() { return engine; }
    
    bool succeeded;
    
    void dump();
    
};

float average(vector<int> &nums);
float standard_dev(vector<int> &nums);

#endif
