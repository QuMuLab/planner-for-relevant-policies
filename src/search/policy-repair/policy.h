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
#include "partial_state.h"
#include "jit.h"

using namespace std;

class GeneratorBase;
class RegressionStep;
class Operator;

class PolicyItem;
class SCNode;

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

    int opt_scd_count;
    int opt_scd_countdown;
    int opt_scd_countdown_step;
    int opt_scd_last_size;

public:

    stack<SCNode> * open_list; // Open list we traverse until strong cyclicity is proven
    set<PartialState> * seen; // Keeps track of the full states we've seen
    vector<PartialState *> * created_states; // Used to clean up the created state objects

    bool opt_scd_skipped;

    Policy();
    ~Policy();

    bool return_if_possible;

    void dump() const;
    void generate_cpp_input(ofstream &outfile) const;

    void update_policy(list<PolicyItem *> &reg_items);
    void add_item(PolicyItem *item);
    void generate_applicable_items(const PartialState &curr, vector<PolicyItem *> &reg_items, bool keep_all, bool only_if_relevant);
    bool check_match(const PartialState &curr, bool keep_all = false);
    RegressionStep *get_best_step(const PartialState &curr);
    bool empty() { return (0 == root); }

    void mark_strong() { score = 1.1; }
    void mark_complete() { complete = true; score = 0.0; }
    void mark_incomplete() { complete = false; score = 0.0; }

    void evaluate();
    double get_score();
    bool better_than(Policy * other);

    int get_size() { return all_items.size(); }
    bool is_complete() { return complete; }
    bool is_strong_cyclic() { return (1.1 == score); }

    void init_scd(bool force_count_reset = false);
    bool step_scd(vector< DeadendTuple * > &failed_states, bool skip_deadends = true);
    bool goal_sc_reachable(const PartialState &curr);

    void dump_human_policy(bool fsap=false);

    void copy_relevant_items(list<PolicyItem *> &items, bool checksc=false);
};


class GeneratorBase {
public:
    virtual ~GeneratorBase() {}
    virtual void dump(string indent) const = 0;
    virtual void generate_cpp_input(ofstream &outfile) const = 0;
    virtual GeneratorBase *update_policy(list<PolicyItem *> &reg_items, set<int> &vars_seen) = 0;
    virtual void generate_applicable_items(const PartialState &curr, vector<PolicyItem *> &reg_items, bool keep_all, bool only_if_relevant) = 0;
    virtual void generate_applicable_items(const PartialState &curr, vector<PolicyItem *> &reg_items, int bound) = 0;
    virtual bool check_match(const PartialState &curr, bool keep_all) = 0;

    GeneratorBase *create_generator(list<PolicyItem *> &reg_items, set<int> &vars_seen);
    int get_best_var(list<PolicyItem *> &reg_items, set<int> &vars_seen);
    bool reg_item_done(PolicyItem *item, set<int> &vars_seen);
};

class GeneratorSwitch : public GeneratorBase {
    int switch_var;
    list<PolicyItem *> immediate_items;
    vector<GeneratorBase *> generator_for_value;
    GeneratorBase *default_generator;

public:
    ~GeneratorSwitch();
    GeneratorSwitch(int switch_variable,
                    list<PolicyItem *> &reg_items,
                    const vector<GeneratorBase *> &gen_for_val,
                    GeneratorBase *default_gen);
    GeneratorSwitch(list<PolicyItem *> &reg_items, set<int> &vars_seen);
    virtual GeneratorBase *update_policy(list<PolicyItem *> &reg_items, set<int> &vars_seen);
    virtual void generate_applicable_items(const PartialState &curr, vector<PolicyItem *> &reg_items, bool keep_all, bool only_if_relevant);
    virtual void generate_applicable_items(const PartialState &curr, vector<PolicyItem *> &reg_items, int bound);
    virtual bool check_match(const PartialState &curr, bool keep_all);
    virtual void dump(string indent) const;
    virtual void generate_cpp_input(ofstream &outfile) const;
};

class GeneratorLeaf : public GeneratorBase {
    list<PolicyItem *> applicable_items;
public:
    GeneratorLeaf(list<PolicyItem *> &reg_items);
    virtual GeneratorBase *update_policy(list<PolicyItem *> &reg_items, set<int> &vars_seen);
    virtual void generate_applicable_items(const PartialState &curr, vector<PolicyItem *> &reg_items, bool keep_all, bool only_if_relevant);
    virtual void generate_applicable_items(const PartialState &curr, vector<PolicyItem *> &reg_items, int bound);
    virtual bool check_match(const PartialState &curr, bool keep_all);
    virtual void dump(string indent) const;
    virtual void generate_cpp_input(ofstream &outfile) const;
};

class GeneratorEmpty : public GeneratorBase {
public:
    virtual GeneratorBase *update_policy(list<PolicyItem *> &reg_items, set<int> &vars_seen);
    virtual void generate_applicable_items(const PartialState &, vector<PolicyItem *> &, bool, bool) {}
    virtual void generate_applicable_items(const PartialState &, vector<PolicyItem *> &, int) {}
    virtual bool check_match(const PartialState &, bool) {return false;}
    virtual void dump(string indent) const;
    virtual void generate_cpp_input(ofstream &outfile) const;
};


#endif
