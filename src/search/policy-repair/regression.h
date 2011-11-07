#ifndef REGRESSION_H
#define REGRESSION_H

#include <iostream>
#include <string>
#include <list>

#include "../globals.h"
#include "../state.h"
#include "../operator.h"
#include "../search_engine.h"
#include "../state_var_t.h"

struct RegressionStep {
    const Operator *op;
    const State *state;
    int distance;
    bool is_goal;

    RegressionStep(const Operator &o, State *s, int d) : op(&o), state(s), distance(d), is_goal(false) {}
    RegressionStep(State *s, int d) : state(s), distance(d), is_goal(true) {}
    ~RegressionStep() {}
    
    string get_op_name();

    void dump() const;
};

list<RegressionStep *> perform_regression(const SearchEngine::Plan &plan, vector<pair<int, int> > goal, int distance, bool create_goal = false);

#endif
