#ifndef POLICY_H
#define POLICY_H

#include <set>
#include <list>
#include <vector>
#include <fstream>
#include <cassert>
#include <map>

#include "regression.h"

using namespace std;

class GeneratorBase;
class Operator;

class Policy {
    GeneratorBase *root;
    
    // private copy constructor to forbid copying;
    // typical idiom for classes with non-trivial destructors
    Policy(const Policy &copy);
    
public:
    Policy();
    Policy(list<RegressionStep *> &reg_steps);
    ~Policy();
    void dump() const;
    void generate_cpp_input(ofstream &outfile) const;
    
    void update_policy(list<RegressionStep *> &reg_steps);
    void generate_applicable_steps(const State &curr, vector<RegressionStep *> &reg_steps);
    RegressionStep *get_best_step(const State &curr);
};

#endif
