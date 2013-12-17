#ifndef POLICY_H
#define POLICY_H

#include <set>
#include <list>
#include <vector>
#include <fstream>
#include <cassert>
#include <map>

#include "regression.h"
#include "simulator.h"
#include "deadend.h"

using namespace std;

class GeneratorBase;
class Operator;

class Policy {
    GeneratorBase *root;
    
    // private copy constructor to forbid copying;
    // typical idiom for classes with non-trivial destructors
    Policy(const Policy &copy);
    
    double score;
    bool complete;
    int size;
    
    void evaluate_random();
    void evaluate_analytical();
    
    list<PolicyItem *> all_items;
    
public:
    Policy();
    Policy(list<PolicyItem *> &reg_items);
    ~Policy();
    
    void dump() const;
    void generate_cpp_input(ofstream &outfile) const;
    
    void update_policy(list<PolicyItem *> &reg_items);
    void generate_applicable_items(const State &curr, vector<PolicyItem *> &reg_items, bool keep_all = false);
    bool check_match(const State &curr, bool keep_all = false);
    RegressionStep *get_best_step(const State &curr);
    bool empty() { return (0 == root); }
    
    void mark_strong() { score = 1.1; }
    void mark_complete() { complete = true; score = 0.0; }
    
    void evaluate();
    double get_score();
    int get_size() { return all_items.size(); }
    bool is_complete() { return complete; }
    bool is_strong_cyclic() { return (1.1 == score); }
    
    void init_scd();
    bool step_scd(vector<State *> &failed_states);
    
    void dump_human_policy();
};

#endif
