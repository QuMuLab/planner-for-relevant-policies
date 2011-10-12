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
    Policy(const Policy &copy);

    //typedef vector<pair<int, int> > Condition;
    //GeneratorBase *construct_recursive(int switchVarNo, vector<RegressionStep *> &reg_steps);
    

    //vector<Condition> conditions;
    //vector<Condition::const_iterator> next_condition_by_op;
    //vector<int> varOrder;

    // private copy constructor to forbid copying;
    // typical idiom for classes with non-trivial destructors
public:
    Policy();
    Policy(list<RegressionStep *> &reg_steps);
    ~Policy();
    void dump() const;
    void generate_cpp_input(ofstream &outfile) const;
    
    void update_policy(list<RegressionStep *> &reg_steps);
};

#endif
