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

#include "policy.h"

class GeneratorBase;

struct PolicyItem {
    State *state;
    Policy *pol;
    GeneratorBase *pol_loc;
    
    PolicyItem(State *s) : state(s) {}
    virtual ~PolicyItem() {}
    virtual string get_name() = 0;
    virtual void dump() const = 0;
    virtual void reposition();
};

struct NondetDeadend : PolicyItem {
    string op_name;
    
    NondetDeadend(State *s, string name) : PolicyItem(s), op_name(name) {}
    
    ~NondetDeadend() {}
    
    string get_name();
    void dump() const;
};

struct RegressableOperator : PolicyItem {
    const Operator *op;
    
    RegressableOperator(const Operator &o, State *s) : PolicyItem(s), op(&o) {}
    
    ~RegressableOperator() {}
    
    string get_name();
    void dump() const;
};

struct RegressionStep : PolicyItem {
    const Operator *op;
    int distance;
    bool is_goal;
    bool is_sc;

    RegressionStep(const Operator &o, State *s, int d) : PolicyItem(s), op(&o), distance(d), is_goal(false), is_sc(false) {}
    RegressionStep(State *s, int d) : PolicyItem(s), distance(d), is_goal(true), is_sc(false) {}
    
    ~RegressionStep() {}
    
    void strengthen(State *s);

    string get_name();
    void dump() const;
    
    bool operator< (const RegressionStep& other) const {
        if (is_sc != other.is_sc)
            return is_sc;
        else
            return distance < other.distance;
    }
};

void generate_regressable_ops();

list<PolicyItem *> perform_regression(const SearchEngine::Plan &plan, vector<pair<int, int> > goal, int distance, bool create_goal = false);

#endif
