#include "../operator.h"
#include "../globals.h"
#include "policy.h"

#include <algorithm>
#include <functional>
#include <iostream>
#include <fstream>
#include <vector>
#include <cassert>
using namespace std;

/* NOTE on possible optimizations:

   * Sharing "GeneratorEmpty" instances might help quite a bit with
     reducing memory usage and possibly even speed, because there are
     bound to be many instance of those. However, it complicates
     deleting the successor generator, and memory doesn't seem to be
     an issue. Speed appears to be fine now, too. So this is probably
     an unnecessary complication.

   * Using slist instead of list led to a further 10% speedup on the
     largest Logistics instance, logistics-98/prob28.pddl. It would of
     course also reduce memory usage. However, it would make the code
     g++-specific, so it's probably not worth it.

*/

class GeneratorBase {
public:
    virtual ~GeneratorBase() {}
    virtual void dump(string indent) const = 0;
    virtual void generate_cpp_input(ofstream &outfile) const = 0;
    virtual GeneratorBase *update_policy(list<RegressionStep *> &reg_steps, set<int> &vars_seen) = 0;
    virtual void generate_applicable_steps(const State &curr, vector<RegressionStep *> &reg_steps) = 0;
    
    GeneratorBase *create_generator(list<RegressionStep *> &reg_steps, set<int> &vars_seen);
    int get_best_var(list<RegressionStep *> &reg_steps, set<int> &vars_seen);
    bool reg_step_done(RegressionStep *op_iter, set<int> &vars_seen);
};

class GeneratorSwitch : public GeneratorBase {
    int switch_var;
    list<RegressionStep *> immediate_steps;
    vector<GeneratorBase *> generator_for_value;
    GeneratorBase *default_generator;
    
public:
    ~GeneratorSwitch();
    GeneratorSwitch(int switch_variable,
                    list<RegressionStep *> &reg_steps,
                    const vector<GeneratorBase *> &gen_for_val,
                    GeneratorBase *default_gen);
    GeneratorSwitch(list<RegressionStep *> &reg_steps, set<int> &vars_seen);
    virtual GeneratorBase *update_policy(list<RegressionStep *> &reg_steps, set<int> &vars_seen);
    virtual void generate_applicable_steps(const State &curr, vector<RegressionStep *> &reg_steps);
    virtual void dump(string indent) const;
    virtual void generate_cpp_input(ofstream &outfile) const;
};

class GeneratorLeaf : public GeneratorBase {
    list<RegressionStep *> applicable_steps;
public:
    ~GeneratorLeaf();
    GeneratorLeaf(list<RegressionStep *> &reg_steps);
    virtual GeneratorBase *update_policy(list<RegressionStep *> &reg_steps, set<int> &vars_seen);
    virtual void generate_applicable_steps(const State &curr, vector<RegressionStep *> &reg_steps);
    virtual void dump(string indent) const;
    virtual void generate_cpp_input(ofstream &outfile) const;
};

class GeneratorEmpty : public GeneratorBase {
public:
    virtual GeneratorBase *update_policy(list<RegressionStep *> &reg_steps, set<int> &vars_seen);
    virtual void generate_applicable_steps(const State &, vector<RegressionStep *> &) {}
    virtual void dump(string indent) const;
    virtual void generate_cpp_input(ofstream &outfile) const;
};


void GeneratorSwitch::generate_applicable_steps(const State &curr, vector<RegressionStep *> &reg_steps) {
    for (list<RegressionStep *>::iterator op_iter = immediate_steps.begin(); op_iter != immediate_steps.end(); ++op_iter)
        reg_steps.push_back(*op_iter);
    
    generator_for_value[curr[switch_var]]->generate_applicable_steps(curr, reg_steps);
    default_generator->generate_applicable_steps(curr, reg_steps);
}

void GeneratorLeaf::generate_applicable_steps(const State &, vector<RegressionStep *> &reg_steps) {
    for (list<RegressionStep *>::iterator op_iter = applicable_steps.begin(); op_iter != applicable_steps.end(); ++op_iter)
        reg_steps.push_back(*op_iter);
}


GeneratorSwitch::GeneratorSwitch(int switch_variable,
                                 list<RegressionStep *> &reg_steps,
                                 const vector<GeneratorBase *> &gen_for_val,
                                 GeneratorBase *default_gen)
    : switch_var(switch_variable),
      generator_for_value(gen_for_val),
      default_generator(default_gen) { immediate_steps.swap(reg_steps); }

GeneratorSwitch::~GeneratorSwitch() {
    for (int i = 0; i < generator_for_value.size(); i++)
        delete generator_for_value[i];
    delete default_generator;
    
    for (list<RegressionStep *>::const_iterator op_iter = immediate_steps.begin();
         op_iter != immediate_steps.end(); ++op_iter)
         delete *op_iter;
}

GeneratorLeaf::~GeneratorLeaf() {
    for (list<RegressionStep *>::const_iterator op_iter = applicable_steps.begin();
         op_iter != applicable_steps.end(); ++op_iter)
         delete *op_iter;
}

void GeneratorSwitch::dump(string indent) const {
    cout << indent << "switch on " << g_variable_name[switch_var] << endl;
    cout << indent << "immediately:" << endl;
    for (list<RegressionStep *>::const_iterator op_iter = immediate_steps.begin();
         op_iter != immediate_steps.end(); ++op_iter)
        cout << indent << (*op_iter)->get_op_name() << endl;
    for (int i = 0; i < g_variable_domain[switch_var]; i++) {
        cout << indent << "case " << i << ":" << endl;
        generator_for_value[i]->dump(indent + "  ");
    }
    cout << indent << "always:" << endl;
    default_generator->dump(indent + "  ");
}

void GeneratorSwitch::generate_cpp_input(ofstream &outfile) const {
    outfile << "switch " << endl;
    outfile << "check " << immediate_steps.size() << endl;
    for (list<RegressionStep *>::const_iterator op_iter = immediate_steps.begin();
         op_iter != immediate_steps.end(); ++op_iter)
        outfile << *op_iter << endl;
    for (int i = 0; i < g_variable_domain[switch_var]; i++) {
        //cout << "case "<<switch_var->get_name()<<" (Level " <<switch_var->get_level() <<
        //  ") has value " << i << ":" << endl;
        generator_for_value[i]->generate_cpp_input(outfile);
    }
    //cout << "always:" << endl;
    default_generator->generate_cpp_input(outfile);
}

GeneratorLeaf::GeneratorLeaf(list<RegressionStep *> &steps) {
    applicable_steps.swap(steps);
}

void GeneratorLeaf::dump(string indent) const {
    for (list<RegressionStep *>::const_iterator op_iter = applicable_steps.begin();
         op_iter != applicable_steps.end(); ++op_iter)
        cout << indent << (*op_iter)->get_op_name() << endl;
}

void GeneratorLeaf::generate_cpp_input(ofstream &outfile) const {
    outfile << "check " << applicable_steps.size() << endl;
    for (list<RegressionStep *>::const_iterator op_iter = applicable_steps.begin();
         op_iter != applicable_steps.end(); ++op_iter)
        outfile << *op_iter << endl;
}

void GeneratorEmpty::dump(string indent) const {
    cout << indent << "<empty>" << endl;
}

void GeneratorEmpty::generate_cpp_input(ofstream &outfile) const {
    outfile << "check 0" << endl;
}


int GeneratorBase::get_best_var(list<RegressionStep *> &reg_steps, set<int> &vars_seen) {
    vector< pair<int,int> > var_count = vector< pair<int,int> >(g_variable_name.size());
    
    for (int i = 0; i < g_variable_name.size(); i++) {
        var_count[i] = pair<int,int>(0, i);
    }
    
    for (list<RegressionStep *>::iterator op_iter = reg_steps.begin(); op_iter != reg_steps.end(); ++op_iter) {
        for (int i = 0; i < g_variable_name.size(); i++) {
            if (state_var_t(-1) != (*((*op_iter)->state))[i]) {
                var_count[i].first++;
            }
        }
    }
    
    sort(var_count.begin(), var_count.end());
    
    for (int i = var_count.size() - 1; i >= 0; i--) {
        if (vars_seen.count(var_count[i].second) <= 0) {
            //cout << "Best var " << var_count[i].second << " with a count of " << var_count[i].first << endl;
            return var_count[i].second;
        }
    }
    
    assert(false);
    return -1;
}

bool GeneratorBase::reg_step_done(RegressionStep *op_iter, set<int> &vars_seen) {
    for (int i = 0; i < g_variable_name.size(); i++) {
        if ((state_var_t(-1) != (*(op_iter->state))[i]) && (vars_seen.count(i) <= 0))
            return false;
    }
    
    return true;
}

GeneratorBase *GeneratorBase::create_generator(list<RegressionStep *> &reg_steps, set<int> &vars_seen) {
    if (reg_steps.empty())
        return new GeneratorEmpty;
    
    // By this point, we are assuming that either /every/ reg_step is
    //  done, or /no/ reg_step is done. Thus we only check the first.
    if (reg_step_done(reg_steps.front(), vars_seen)) {
        return new GeneratorLeaf(reg_steps);
    } else {
        return new GeneratorSwitch(reg_steps, vars_seen);
    }
}

GeneratorSwitch::GeneratorSwitch(list<RegressionStep *> &reg_steps, set<int> &vars_seen) {
    switch_var = get_best_var(reg_steps, vars_seen);
    
    vector< list<RegressionStep *> > value_steps;
    list<RegressionStep *> default_steps;
    
    // Initialize the value_steps
    for (int i = 0; i < g_variable_domain[switch_var]; i++)
        value_steps.push_back(list<RegressionStep *>());
    
    // Sort out the regression steps
    for (list<RegressionStep *>::iterator op_iter = reg_steps.begin(); op_iter != reg_steps.end(); ++op_iter) {
        if (reg_step_done(*op_iter, vars_seen)) {
            immediate_steps.push_back(*op_iter);
        } else if (state_var_t(-1) != (*((*op_iter)->state))[switch_var]) {
            value_steps[(*((*op_iter)->state))[switch_var]].push_back(*op_iter);
        } else { // == -1
            default_steps.push_back(*op_iter);
        }
    }
    
    vars_seen.insert(switch_var);
    
    // Create the switch generators
    for (int i = 0; i < value_steps.size(); i++) {
        generator_for_value.push_back(create_generator(value_steps[i], vars_seen));
    }
    
    // Create the default generator
    default_generator = create_generator(default_steps, vars_seen);
    
    vars_seen.erase(switch_var);
}

GeneratorBase *GeneratorSwitch::update_policy(list<RegressionStep *> &reg_steps, set<int> &vars_seen) {
    vector< list<RegressionStep *> > value_steps;
    list<RegressionStep *> default_steps;
    
    // Initialize the value_steps
    for (int i = 0; i < g_variable_domain[switch_var]; i++)
        value_steps.push_back(list<RegressionStep *>());
    
    // Sort out the regression steps
    for (list<RegressionStep *>::iterator op_iter = reg_steps.begin(); op_iter != reg_steps.end(); ++op_iter) {
        if (reg_step_done(*op_iter, vars_seen)) {
            immediate_steps.push_back(*op_iter);
        } else if (state_var_t(-1) != (*((*op_iter)->state))[switch_var]) {
            value_steps[(*((*op_iter)->state))[switch_var]].push_back(*op_iter);
        } else { // == -1
            default_steps.push_back(*op_iter);
        }
    }
    
    vars_seen.insert(switch_var);
    
    // Update the switch generators
    for (int i = 0; i < value_steps.size(); i++) {
        GeneratorBase *newGen = generator_for_value[i]->update_policy(value_steps[i], vars_seen);
        if (NULL != newGen) {
            delete generator_for_value[i];
            generator_for_value[i] = newGen;
        }
    }
    
    // Update the default generator
    GeneratorBase *newGen = default_generator->update_policy(default_steps, vars_seen);
    if (NULL != newGen) {
        delete default_generator;
        default_generator = newGen;
    }
    
    vars_seen.erase(switch_var);
    
    return NULL;
}

GeneratorBase *GeneratorLeaf::update_policy(list<RegressionStep *> &reg_steps, set<int> &vars_seen) {
    if (reg_steps.empty())
        return NULL;
    
    bool all_done = true;
    for (list<RegressionStep *>::iterator op_iter = reg_steps.begin(); op_iter != reg_steps.end(); ++op_iter) {
        if (!reg_step_done(*op_iter, vars_seen)) {
            all_done = false;
            break;
        }
    }
    
    if (all_done) {
        applicable_steps.splice(applicable_steps.end(), reg_steps);
        return NULL;
    } else {
        reg_steps.splice(reg_steps.end(), applicable_steps);
        return new GeneratorSwitch(reg_steps, vars_seen);
    }
}

GeneratorBase *GeneratorEmpty::update_policy(list<RegressionStep *> &reg_steps, set<int> &vars_seen) {
    if (reg_steps.empty())
        return NULL;
    
    bool all_done = true;
    for (list<RegressionStep *>::iterator op_iter = reg_steps.begin(); op_iter != reg_steps.end(); ++op_iter) {
        if (!reg_step_done(*op_iter, vars_seen)) {
            all_done = false;
            break;
        }
    }
    
    if (all_done)
        return new GeneratorLeaf(reg_steps);
    else
        return new GeneratorSwitch(reg_steps, vars_seen);
}

Policy::Policy(list<RegressionStep *> &reg_steps) {
    g_timer_policy_build.resume();
    set<int> vars_seen;
    root = new GeneratorSwitch(reg_steps, vars_seen);
    g_timer_policy_build.stop();
    
    score = 0.0;
    
}

void Policy::update_policy(list<RegressionStep *> &reg_steps) {
    g_timer_policy_build.resume();
    set<int> vars_seen;
    if (root)
        root->update_policy(reg_steps, vars_seen);
    else
        root = new GeneratorSwitch(reg_steps, vars_seen);
    g_timer_policy_build.stop();
}

void Policy::generate_applicable_steps(const State &curr, vector<RegressionStep *> &reg_steps) {
    root->generate_applicable_steps(curr, reg_steps);
}

RegressionStep *Policy::get_best_step(const State &curr) {
    
    if (0 == root)
        return 0;
    
    g_timer_policy_use.resume();
    vector<RegressionStep *> current_steps;
    generate_applicable_steps(curr, current_steps);
    
    if (0 == current_steps.size()) {
        g_timer_policy_use.stop();
        return 0;
    }
    
    int best_index = 0;
    int best_val = current_steps[0]->distance;
    
    for (int i = 0; i < current_steps.size(); i++) {
        if (current_steps[i]->distance < best_val) {
            best_val = current_steps[i]->distance;
            best_index = i;
        }
    }
    g_timer_policy_use.stop();
    return current_steps[best_index];
}

Policy::Policy() {
    root = 0;
    score = 0.0;
}

Policy::~Policy() {
    if (root)
        delete root;
}

void Policy::dump() const {
    cout << "Policy:" << endl;
    root->dump("  ");
}
void Policy::generate_cpp_input(ofstream &outfile) const {
    root->generate_cpp_input(outfile);
}



double Policy::get_score() {
    if (0.0 == score)
        evaluate();
    return score;
}

void Policy::evaluate() {
    if (1.0 == score)
        return;
    
    g_timer_policy_eval.resume();
    
    //evaluate_analytical();
    evaluate_random();
    
    g_timer_policy_eval.stop();
}

void Policy::evaluate_analytical() {
    
}

void Policy::evaluate_random() {
    Simulator *sim = new Simulator(false);
    int succeeded = 0;
    int NUMTRIALS = 1000;
    for (int i = 0; i < NUMTRIALS; i++) {
        sim->run_once(true, this);
        if (sim->succeeded)
            succeeded++;
    }
    score = double(succeeded) / double(NUMTRIALS);
}

