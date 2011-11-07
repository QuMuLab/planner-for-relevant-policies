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

using namespace std;

class GeneratorBase;
class Operator;

class Policy {
    GeneratorBase *root;
    
    // private copy constructor to forbid copying;
    // typical idiom for classes with non-trivial destructors
    Policy(const Policy &copy);
    
    double score;
    int size;
    
    void evaluate_random();
    void evaluate_analytical();
    
    list<RegressionStep *> all_steps;
    
public:
    Policy();
    Policy(list<RegressionStep *> &reg_steps);
    ~Policy();
    void dump() const;
    void generate_cpp_input(ofstream &outfile) const;
    
    void update_policy(list<RegressionStep *> &reg_steps);
    void generate_applicable_steps(const State &curr, vector<RegressionStep *> &reg_steps);
    RegressionStep *get_best_step(const State &curr);
    bool empty() { return (0 == root); }
    
    void mark_strong() { score = 1.0; }
    
    void evaluate();
    double get_score();
    int get_size() { return all_steps.size(); }
};

#endif
