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
    bool relevant;
    int _generality;
    
    PolicyItem(PartialState *s) : state(s), pol(0), relevant(false), _generality(-1) {}
    virtual ~PolicyItem() {}
    virtual string get_name() = 0;
    virtual void dump() const = 0;
    
    int generality();
    
};

struct NondetDeadend : PolicyItem {
    //string op_name;
    int op_index;
    
    //NondetDeadend(PartialState *s, int index, string name) : PolicyItem(s), op_index(index), op_name(name) {}
    NondetDeadend(PartialState *s, int index) : PolicyItem(s), op_index(index) {}
    
    ~NondetDeadend() {}
    
    string get_name();
    int get_index();
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
    int step_id;

    RegressionStep(const Operator &o, PartialState *s, int d) : PolicyItem(s), op(&o), distance(d), is_goal(false), is_sc(false), step_id(g_num_regsteps++) {}
    RegressionStep(PartialState *s, int d) : PolicyItem(s), distance(d), is_goal(true), is_sc(false), step_id(g_num_regsteps++) {}
    
    ~RegressionStep() {}
    
    void strengthen(PartialState *s);

    string get_name();
    void dump() const;
    
    bool operator< (const RegressionStep& other) const {
        if (is_sc != other.is_sc)
            return is_sc;
        else if (distance != other.distance)
            return distance < other.distance;
        else
            return step_id < other.step_id;
    }
};

void generate_regressable_ops();

list<PolicyItem *> perform_regression(const SearchEngine::Plan &plan, vector<pair<int, int> > goal, int distance, bool create_goal = false);

#endif
