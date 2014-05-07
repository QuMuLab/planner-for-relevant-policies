#ifndef REGRESSION_H
#define REGRESSION_H

#include <iostream>
#include <string>
#include <list>

#include "../globals.h"
#include "../state.h"
#include "../operator.h"
#include "../search_engine.h"

#include "policy.h"
#include "partial_state.h"

class GeneratorBase;

using namespace std;

struct PolicyItem {
    PartialState *state;
    Policy *pol;
    
    PolicyItem(PartialState *s) : state(s), pol(0) {}
    virtual ~PolicyItem() {}
    virtual string get_name() = 0;
    virtual void dump() const = 0;
};

struct NondetDeadend : PolicyItem {
    string op_name;
    
    NondetDeadend(PartialState *s, string name) : PolicyItem(s), op_name(name) {}
    
    ~NondetDeadend() {}
    
    string get_name();
    void dump() const;
};

struct RegressableOperator : PolicyItem {
    const Operator *op;
    
    RegressableOperator(const Operator &o, PartialState *s) : PolicyItem(s), op(&o) {}
    
    ~RegressableOperator() {}
    
    string get_name();
    void dump() const;
};

struct RegressionStep : PolicyItem {
    const Operator *op;
    int distance;
    bool is_goal;
    bool is_sc;

    RegressionStep(const Operator &o, PartialState *s, int d) : PolicyItem(s), op(&o), distance(d), is_goal(false), is_sc(false) {}
    RegressionStep(PartialState *s, int d) : PolicyItem(s), distance(d), is_goal(true), is_sc(false) {}
    
    ~RegressionStep() {}
    
    void strengthen(PartialState *s);

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
