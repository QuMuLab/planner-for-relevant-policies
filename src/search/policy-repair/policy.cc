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
    virtual GeneratorBase *update_policy(list<PolicyItem *> &reg_items, set<int> &vars_seen) = 0;
    virtual void generate_applicable_items(const State &curr, vector<PolicyItem *> &reg_items, bool keep_all) = 0;
    virtual void generate_applicable_items(const State &curr, vector<PolicyItem *> &reg_items, int bound) = 0;
    virtual bool check_match(const State &curr, bool keep_all) = 0;
    
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
    virtual void generate_applicable_items(const State &curr, vector<PolicyItem *> &reg_items, bool keep_all);
    virtual void generate_applicable_items(const State &curr, vector<PolicyItem *> &reg_items, int bound);
    virtual bool check_match(const State &curr, bool keep_all);
    virtual void dump(string indent) const;
    virtual void generate_cpp_input(ofstream &outfile) const;
};

class GeneratorLeaf : public GeneratorBase {
    list<PolicyItem *> applicable_items;
public:
    GeneratorLeaf(list<PolicyItem *> &reg_items);
    virtual GeneratorBase *update_policy(list<PolicyItem *> &reg_items, set<int> &vars_seen);
    virtual void generate_applicable_items(const State &curr, vector<PolicyItem *> &reg_items, bool keep_all);
    virtual void generate_applicable_items(const State &curr, vector<PolicyItem *> &reg_items, int bound);
    virtual bool check_match(const State &curr, bool keep_all);
    virtual void dump(string indent) const;
    virtual void generate_cpp_input(ofstream &outfile) const;
};

class GeneratorEmpty : public GeneratorBase {
public:
    virtual GeneratorBase *update_policy(list<PolicyItem *> &reg_items, set<int> &vars_seen);
    virtual void generate_applicable_items(const State &, vector<PolicyItem *> &, bool) {}
    virtual void generate_applicable_items(const State &, vector<PolicyItem *> &, int) {}
    virtual bool check_match(const State &, bool) {return false;}
    virtual void dump(string indent) const;
    virtual void generate_cpp_input(ofstream &outfile) const;
};


bool GeneratorSwitch::check_match(const State &curr, bool keep_all) {
    if (immediate_items.size() > 0)
        return true;
    
    if ((curr[switch_var] != state_var_t(-1)) && (generator_for_value[curr[switch_var]]->check_match(curr, keep_all)))
        return true;
    
    if ((curr[switch_var] == state_var_t(-1)) && keep_all) {
        for (int i = 0; i < g_variable_domain[switch_var]; i++) {
            if (generator_for_value[i]->check_match(curr, keep_all))
                return true;
        }
    }
    
    if (default_generator->check_match(curr, keep_all))
        return true;
    
    return false;
}

void GeneratorSwitch::generate_applicable_items(const State &curr, vector<PolicyItem *> &reg_items, bool keep_all) {
    for (list<PolicyItem *>::iterator op_iter = immediate_items.begin(); op_iter != immediate_items.end(); ++op_iter)
        reg_items.push_back(*op_iter);
    
    if (curr[switch_var] != state_var_t(-1))
        generator_for_value[curr[switch_var]]->generate_applicable_items(curr, reg_items, keep_all);
    else if (keep_all) {
        for (int i = 0; i < g_variable_domain[switch_var]; i++) {
            generator_for_value[i]->generate_applicable_items(curr, reg_items, keep_all);
        }
    }
    
    default_generator->generate_applicable_items(curr, reg_items, keep_all);
}

void GeneratorSwitch::generate_applicable_items(const State &curr, vector<PolicyItem *> &reg_items, int bound) {
    int best_val = 9999999;
    PolicyItem * best_rs = NULL;
    for (list<PolicyItem *>::iterator op_iter = immediate_items.begin(); op_iter != immediate_items.end(); ++op_iter)
    {
        int cur_val = ((RegressionStep *)(*op_iter))->distance;
        if (cur_val < best_val) {
            best_val = cur_val;
            best_rs = *op_iter;
        }
    }
    if (best_val <= bound)
        reg_items.push_back(best_rs);
    
    if (curr[switch_var] == state_var_t(-1)) {
        for (int i = 0; i < g_variable_domain[switch_var]; i++) {
            generator_for_value[i]->generate_applicable_items(curr, reg_items, bound);
        }
    } else {
        generator_for_value[curr[switch_var]]->generate_applicable_items(curr, reg_items, bound);
    }
    default_generator->generate_applicable_items(curr, reg_items, bound);
}

bool GeneratorLeaf::check_match(const State &, bool) {
    if (applicable_items.size() > 0)
        return true;
    else
        return false;
}

void GeneratorLeaf::generate_applicable_items(const State &, vector<PolicyItem *> &reg_items, bool) {
    for (list<PolicyItem *>::iterator op_iter = applicable_items.begin(); op_iter != applicable_items.end(); ++op_iter)
        reg_items.push_back(*op_iter);
}

void GeneratorLeaf::generate_applicable_items(const State &, vector<PolicyItem *> &reg_items, int bound) {
    int best_val = 9999999;
    PolicyItem * best_rs = NULL;
    for (list<PolicyItem *>::iterator op_iter = applicable_items.begin(); op_iter != applicable_items.end(); ++op_iter)
    {
        int cur_val = ((RegressionStep *)(*op_iter))->distance;
        if (cur_val < best_val) {
            best_val = cur_val;
            best_rs = *op_iter;
        }
    }
    if (best_val <= bound)
        reg_items.push_back(best_rs);
}



GeneratorSwitch::GeneratorSwitch(int switch_variable,
                                 list<PolicyItem *> &reg_items,
                                 const vector<GeneratorBase *> &gen_for_val,
                                 GeneratorBase *default_gen)
    : switch_var(switch_variable),
      generator_for_value(gen_for_val),
      default_generator(default_gen) { immediate_items.swap(reg_items); }

GeneratorSwitch::~GeneratorSwitch() {
    for (int i = 0; i < generator_for_value.size(); i++)
        delete generator_for_value[i];
    delete default_generator;
}

void GeneratorSwitch::dump(string indent) const {
    cout << indent << "switch on " << g_variable_name[switch_var] << endl;
    cout << indent << "immediately:" << endl;
    for (list<PolicyItem *>::const_iterator op_iter = immediate_items.begin();
         op_iter != immediate_items.end(); ++op_iter)
        cout << indent << (*op_iter)->get_name() << endl;
    for (int i = 0; i < g_variable_domain[switch_var]; i++) {
        cout << indent << "case " << i << ":" << endl;
        generator_for_value[i]->dump(indent + "  ");
    }
    cout << indent << "always:" << endl;
    default_generator->dump(indent + "  ");
}

void GeneratorSwitch::generate_cpp_input(ofstream &outfile) const {
    outfile << "switch " << switch_var << endl;
    outfile << "check " << immediate_items.size() << endl;
    for (list<PolicyItem *>::const_iterator op_iter = immediate_items.begin();
         op_iter != immediate_items.end(); ++op_iter)
        outfile << (*op_iter)->get_name() << endl;
    for (int i = 0; i < g_variable_domain[switch_var]; i++) {
        //cout << "case "<<switch_var->get_name()<<" (Level " <<switch_var->get_level() <<
        //  ") has value " << i << ":" << endl;
        generator_for_value[i]->generate_cpp_input(outfile);
    }
    //cout << "always:" << endl;
    default_generator->generate_cpp_input(outfile);
}

GeneratorLeaf::GeneratorLeaf(list<PolicyItem *> &items) {
    applicable_items.swap(items);
}

void GeneratorLeaf::dump(string indent) const {
    for (list<PolicyItem *>::const_iterator op_iter = applicable_items.begin();
         op_iter != applicable_items.end(); ++op_iter)
        cout << indent << (*op_iter)->get_name() << endl;
}

void GeneratorLeaf::generate_cpp_input(ofstream &outfile) const {
    outfile << "check " << applicable_items.size() << endl;
    for (list<PolicyItem *>::const_iterator op_iter = applicable_items.begin();
         op_iter != applicable_items.end(); ++op_iter)
        outfile << (*op_iter)->get_name() << endl;
}

void GeneratorEmpty::dump(string indent) const {
    cout << indent << "<empty>" << endl;
}

void GeneratorEmpty::generate_cpp_input(ofstream &outfile) const {
    outfile << "check 0" << endl;
}


int GeneratorBase::get_best_var(list<PolicyItem *> &reg_items, set<int> &vars_seen) {
    vector< pair<int,int> > var_count = vector< pair<int,int> >(g_variable_name.size());
    
    for (int i = 0; i < g_variable_name.size(); i++) {
        var_count[i] = pair<int,int>(0, i);
    }
    
    for (list<PolicyItem *>::iterator op_iter = reg_items.begin(); op_iter != reg_items.end(); ++op_iter) {
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

bool GeneratorBase::reg_item_done(PolicyItem *op_iter, set<int> &vars_seen) {
    for (int i = 0; i < g_variable_name.size(); i++) {
        if ((state_var_t(-1) != (*(op_iter->state))[i]) && (vars_seen.count(i) <= 0))
            return false;
    }
    
    return true;
}

GeneratorBase *GeneratorBase::create_generator(list<PolicyItem *> &reg_items, set<int> &vars_seen) {
    if (reg_items.empty())
        return new GeneratorEmpty;
    
    // If every item is done, then we create a leaf node
    bool all_done = true;
    for (list<PolicyItem *>::iterator op_iter = reg_items.begin(); all_done && (op_iter != reg_items.end()); ++op_iter) {
        if (!(reg_item_done(*op_iter, vars_seen))) {
            all_done = false;
        }
    }
    
    if (all_done) {
        return new GeneratorLeaf(reg_items);
    } else {
        return new GeneratorSwitch(reg_items, vars_seen);
    }
}

GeneratorSwitch::GeneratorSwitch(list<PolicyItem *> &reg_items, set<int> &vars_seen) {
    switch_var = get_best_var(reg_items, vars_seen);
    
    vector< list<PolicyItem *> > value_items;
    list<PolicyItem *> default_items;
    
    // Initialize the value_items
    for (int i = 0; i < g_variable_domain[switch_var]; i++)
        value_items.push_back(list<PolicyItem *>());
    
    // Sort out the regression items
    for (list<PolicyItem *>::iterator op_iter = reg_items.begin(); op_iter != reg_items.end(); ++op_iter) {
        if (reg_item_done(*op_iter, vars_seen)) {
            immediate_items.push_back(*op_iter);
        } else if (state_var_t(-1) != (*((*op_iter)->state))[switch_var]) {
            value_items[(*((*op_iter)->state))[switch_var]].push_back(*op_iter);
        } else { // == -1
            default_items.push_back(*op_iter);
        }
    }
    
    vars_seen.insert(switch_var);
    
    // Create the switch generators
    for (int i = 0; i < value_items.size(); i++) {
        generator_for_value.push_back(create_generator(value_items[i], vars_seen));
    }
    
    // Create the default generator
    default_generator = create_generator(default_items, vars_seen);
    
    vars_seen.erase(switch_var);
}

GeneratorBase *GeneratorSwitch::update_policy(list<PolicyItem *> &reg_items, set<int> &vars_seen) {
    vector< list<PolicyItem *> > value_items;
    list<PolicyItem *> default_items;
    
    // Initialize the value_items
    for (int i = 0; i < g_variable_domain[switch_var]; i++)
        value_items.push_back(list<PolicyItem *>());
    
    // Sort out the regression items
    for (list<PolicyItem *>::iterator op_iter = reg_items.begin(); op_iter != reg_items.end(); ++op_iter) {
        if (reg_item_done(*op_iter, vars_seen)) {
            immediate_items.push_back(*op_iter);
        } else if (state_var_t(-1) != (*((*op_iter)->state))[switch_var]) {
            value_items[(*((*op_iter)->state))[switch_var]].push_back(*op_iter);
        } else { // == -1
            default_items.push_back(*op_iter);
        }
    }
    
    vars_seen.insert(switch_var);
    
    // Update the switch generators
    for (int i = 0; i < value_items.size(); i++) {
        GeneratorBase *newGen = generator_for_value[i]->update_policy(value_items[i], vars_seen);
        if (NULL != newGen) {
            delete generator_for_value[i];
            generator_for_value[i] = newGen;
        }
    }
    
    // Update the default generator
    GeneratorBase *newGen = default_generator->update_policy(default_items, vars_seen);
    if (NULL != newGen) {
        delete default_generator;
        default_generator = newGen;
    }
    
    vars_seen.erase(switch_var);
    
    return NULL;
}

GeneratorBase *GeneratorLeaf::update_policy(list<PolicyItem *> &reg_items, set<int> &vars_seen) {
    if (reg_items.empty())
        return NULL;
    
    bool all_done = true;
    for (list<PolicyItem *>::iterator op_iter = reg_items.begin(); op_iter != reg_items.end(); ++op_iter) {
        if (!reg_item_done(*op_iter, vars_seen)) {
            all_done = false;
            break;
        }
    }
    
    if (all_done) {
        applicable_items.splice(applicable_items.end(), reg_items);
        return NULL;
    } else {
        reg_items.splice(reg_items.end(), applicable_items);
        return new GeneratorSwitch(reg_items, vars_seen);
    }
}

GeneratorBase *GeneratorEmpty::update_policy(list<PolicyItem *> &reg_items, set<int> &vars_seen) {
    if (reg_items.empty())
        return NULL;
    
    bool all_done = true;
    for (list<PolicyItem *>::iterator op_iter = reg_items.begin(); op_iter != reg_items.end(); ++op_iter) {
        if (!reg_item_done(*op_iter, vars_seen)) {
            all_done = false;
            break;
        }
    }
    
    if (all_done)
        return new GeneratorLeaf(reg_items);
    else
        return new GeneratorSwitch(reg_items, vars_seen);
}

Policy::Policy(list<PolicyItem *> &reg_items) {
    g_timer_policy_build.resume();
    
    set<int> vars_seen;
    root = new GeneratorSwitch(reg_items, vars_seen);
    all_items = reg_items;
    
    g_timer_policy_build.stop();
    
    score = 0.0;
    complete = false;
    
}

void Policy::update_policy(list<PolicyItem *> &reg_items) {
    g_timer_policy_build.resume();

    // Reset the score since a change is being made to the policy
    score = 0.0;

    set<int> vars_seen;
    if (root)
        root->update_policy(reg_items, vars_seen);
    else
        root = new GeneratorSwitch(reg_items, vars_seen);
    all_items.insert(all_items.end(), reg_items.begin(), reg_items.end());
    
    g_timer_policy_build.stop();
}

void Policy::generate_applicable_items(const State &curr, vector<PolicyItem *> &reg_items, bool keep_all) {
    if (root)
        root->generate_applicable_items(curr, reg_items, keep_all);
}

bool Policy::check_match(const State &curr, bool keep_all) {
    if (root)
        return root->check_match(curr, keep_all);
    else
        return false;
}

RegressionStep *Policy::get_best_step(const State &curr) {
    
    if (0 == root)
        return 0;
    
    g_timer_policy_use.resume();
    vector<PolicyItem *> current_steps;
    generate_applicable_items(curr, current_steps);
    
    if (0 == current_steps.size()) {
        g_timer_policy_use.stop();
        return 0;
    }
    
    // We should only return steps that aren't forbidden
    vector<PolicyItem *> forbidden_items;
    set<string> forbidden;
    if (!complete)
        g_deadend_policy->generate_applicable_items(curr, forbidden_items);
    for (int i = 0; i < forbidden_items.size(); i++)
        forbidden.insert(((NondetDeadend*)(forbidden_items[i]))->op_name);
    
    int best_index = -1;
    int best_val = 999999; // This will only be invalid if a plan length was > 10^6
    
    int best_sc_index = -1;
    int best_sc_val = 999999;
    
    for (int i = 0; i < current_steps.size(); i++) {
        if (((RegressionStep*)(current_steps[i]))->is_goal ||
            (0 == forbidden.count(((RegressionStep*)(current_steps[i]))->op->get_nondet_name()))) {
            int cur_val = ((RegressionStep*)(current_steps[i]))->distance;
            
            if (cur_val < best_val) {
                best_val = cur_val;
                best_index = i;
            }
            
            if (g_optimized_scd &&
                ((RegressionStep*)(current_steps[i]))->is_sc &&
                (cur_val < best_sc_val)) {
                best_sc_val = cur_val;
                best_sc_index = i;
            }
        }
    }
    g_timer_policy_use.stop();
    
    if (-1 == best_index)
        return 0;
    else if (g_optimized_scd && (-1 != best_sc_index))
        return (RegressionStep*)(current_steps[best_sc_index]);
    else
        return (RegressionStep*)(current_steps[best_index]);
}

Policy::Policy() {
    root = 0;
    score = 0.0;
    complete = false;
}

Policy::~Policy() {
    if (root)
        delete root;
    
    for (list<PolicyItem *>::const_iterator op_iter = all_items.begin();
         op_iter != all_items.end(); ++op_iter)
         delete *op_iter;
}

void Policy::dump() const {
    cout << "Policy:" << endl;
    //root->dump("  ");
    for (list<PolicyItem *>::const_iterator op_iter = all_items.begin();
         op_iter != all_items.end(); ++op_iter)
         (*op_iter)->dump();
}
void Policy::generate_cpp_input(ofstream &outfile) const {
    root->generate_cpp_input(outfile);
}



double Policy::get_score() {
    if (0.0 == score)
        evaluate();
    return min(score, 1.0);
}

void Policy::evaluate() {
    if (1.0 <= score)
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



void Policy::init_scd() {
    for (list<PolicyItem *>::const_iterator op_iter = all_items.begin();
         op_iter != all_items.end(); ++op_iter)
         ((RegressionStep *)(*op_iter))->is_sc = true;
}

bool Policy::step_scd(vector<State *> &failed_states) {
    bool made_change = false;
    for (list<PolicyItem *>::const_iterator op_iter = all_items.begin();
         op_iter != all_items.end(); ++op_iter)
    {
        RegressionStep *rs = (RegressionStep *)(*op_iter);
        
        if (rs->is_sc && !(rs->is_goal)) {
            
            for (int i = 0; i < g_nondet_mapping[rs->op->get_nondet_name()].size(); i++) {
				
                // We use the sc_state for computing the guaranteed items, rather than
                //  the original state for the regression step. The sc_state will be a
                //  superset of the original state that includes the regression of newly
                //  closed leafs from the jic compilation phase. This may increase the
                //  number of regression steps we are guaranteed to see in a state matching
                //  succ_state, but as long as we remain in parts of the policy that return
                //  regression steps based on their sc_state then this will be valid.
                State *succ_state = new State(*(rs->sc_state), *(g_nondet_mapping[rs->op->get_nondet_name()][i]));
                vector<PolicyItem *> guaranteed_steps;
                root->generate_applicable_items(*succ_state, guaranteed_steps, false);
                
                
                // We need at least one guaranteed step to be sure that we can continue
                //  executing. The one exception is if the state is already known to be
                //  a deadend, in which case we can assume that it will be handled by
                //  the jic compiler.
                if (0 == guaranteed_steps.size()) {
                    bool is_failed_state = false;
                    for (int j = 0; j < failed_states.size(); j++) {
                        // Unfortunately, we can't just check the states equivalence,
                        //  since the succ_state is a partial state. So we instead check
                        //  that succ_state entails the failed state.
                        is_failed_state = true;
                        for (int k = 0; k < g_variable_name.size(); k++) {
                            if (((*(failed_states[j]))[k] != state_var_t(-1)) &&
                                ((*(failed_states[j]))[k] != (*succ_state)[k])) {
                                is_failed_state = false;
                                break;
                            }
                        }
                        
                        if (is_failed_state)
                            break;

                    }
                    
                    // We may have stumbled across a new failed state, in which
                    //  case, we can add it to the list and assume it will be
                    //  handled later.
                    if (!is_failed_state) {
                        if (is_deadend(*succ_state)) {
                            if (g_generalize_deadends)
                                generalize_deadend(*succ_state);
                                
                            // Use a new state since succ_state is deleted below
                            failed_states.push_back(new State(*succ_state));
                            is_failed_state = true;
                        }
                    }
                    
                    
                    // If succ_state isn't a failed state (as far as we're aware
                    //  of), then it may be reached during rollout. The possibility
                    //  of not handling the reached state means that this can't be
                    //  strongly cyclic. The break take us to the next regression
                    //  step to check (i.e., no need to check the rest of the action
                    //  outcomes for the current regression step).
                    if (!is_failed_state) {
                        rs->is_sc = false;
                        made_change = true;
                        delete succ_state;
                        break;
                    }
                }
                
                // We only consider the possible steps that have a cheaper cost than
                //  the cheapest guaranteed cost. We will be returning the cheapest
                //  cost in a get_best_step, so only those regsteps with a chance of
                //  overiding all guaranteed regsteps must be looked at.
                int min_cost = 999999; // This will only be too low if we found a plan of length 10^6
                int min_sc_cost = 999999;
                for (int j = 0; j < guaranteed_steps.size(); j++) {
                    
                    if (((RegressionStep *)guaranteed_steps[j])->distance < min_cost)
                        min_cost = ((RegressionStep *)guaranteed_steps[j])->distance;
                        
					if ((((RegressionStep *)guaranteed_steps[j])->distance < min_sc_cost) &&
						((RegressionStep *)guaranteed_steps[j])->is_sc)
                        min_sc_cost = ((RegressionStep *)guaranteed_steps[j])->distance;
                
                }
                
                // The guaranteed step can't be further from the goal than
                //  the current candidate strong cyclic pair. Otherwise,
                //  we could get an unsound loop of presumed strong cyclicity.
                if ((999999 != min_sc_cost) && (min_sc_cost >= rs->distance)) {
					//cout << "Min sc cost = " << min_sc_cost << endl;
					rs->is_sc = false;
					made_change = true;
					i = g_nondet_mapping[rs->op->get_nondet_name()].size();
					
				} else {
                
					vector<PolicyItem *> possible_steps;
					root->generate_applicable_items(*succ_state, possible_steps, min_cost);
					//root->generate_applicable_items(*succ_state, possible_steps, true);
					
					//cout << "Guaranteed steps / Possible steps: " << guaranteed_steps.size() << " / " << possible_steps.size() << endl;
					//cout << "Min cost = " << min_cost << endl;
					
					// If any possible successor state that we reach has a matching
					//  regression step that isn't strongly cyclic, then neither are
					//  we. A place for optimization is to prune the set of possible
					//  regression steps returned -- if we can guarantee that the call
					//  to the get_best_step function won't return a regression step,
					//  then we need not confirm it is strongly cyclic.
					for (int j = 0; j < possible_steps.size(); j++) {
						if (!(((RegressionStep *)possible_steps[j])->is_sc)) {
							rs->is_sc = false;
							made_change = true;
							i = g_nondet_mapping[rs->op->get_nondet_name()].size();
							j = possible_steps.size();
						}
					}
					
					/*if (rs->is_sc && (999999 != min_sc_cost) && (min_sc_cost > rs->distance)) {
						cout << "New prune at distance (" << min_sc_cost << " vs " << rs->distance << ")..." << endl;
						rs->dump();
					}*/
					
				}
                
                delete succ_state;
            }
        }
    }
    return made_change;
}

bool regstep_compare(PolicyItem* first, PolicyItem* second) {
    if (((RegressionStep*)first)->is_sc != ((RegressionStep*)second)->is_sc)
		return ((RegressionStep*)first)->is_sc;
	else
		return ((RegressionStep*)first)->distance < ((RegressionStep*)second)->distance;
}
void Policy::dump_human_policy() {
	
	all_items.sort(regstep_compare);
	
    fstream outfile;
    outfile.open("policy.out", ios::out);
        
    for (list<PolicyItem *>::const_iterator op_iter = all_items.begin();
         op_iter != all_items.end(); ++op_iter) {
        
        outfile << "\nIf holds:";
        for (int i = 0; i < g_variable_domain.size(); i++) {
			if (state_var_t(-1) != (*(((RegressionStep*)(*op_iter))->sc_state))[i]) {
				outfile << " ";
				outfile << g_variable_name[i] << ":"
				     << static_cast<int>((*(((RegressionStep*)(*op_iter))->sc_state))[i]);
			}
		}
		outfile << endl;
        outfile << "Execute: " << ((RegressionStep*)(*op_iter))->get_name() << endl;
    }
    
    outfile.close();
}

