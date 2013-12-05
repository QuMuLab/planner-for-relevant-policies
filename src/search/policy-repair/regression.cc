#include "regression.h"
#include "policy.h"

void RegressionStep::dump() const {
    cout << "Regression Step (" << distance << ")" << endl;
    cout << " SC: " << is_sc << endl;
    if (!is_goal) {
        cout << " -{ Operator }-" << endl;
        op->dump();
    } else {
        cout << " -{ Goal }-" << endl;
    }
    cout << "\n -{ State }-" << endl;
    state->dump_fdr();
    cout << "" << endl;
}

string RegressionStep::get_name() {
    if (is_goal)
        return "goal / SC / d=0";
    else
        return op->get_nondet_name() + " / " + (is_sc ? "SC" : "NSC") + " / d=" + static_cast<ostringstream*>( &(ostringstream() << distance) )->str();
}


void NondetDeadend::dump() const {
    cout << "Non-deterministic deadend:" << endl;
    cout << "Operator: " << op_name << endl;
    cout << " -{ State }-" << endl;
    state->dump_fdr();
    cout << "" << endl;
}

string NondetDeadend::get_name() {
    return op_name;
}


void RegressableOperator::dump() const {
    cout << "Regressable operator:" << endl;
    cout << " -{ Operator }-" << endl;
    op->dump();
    cout << " -{ State }-" << endl;
    state->dump_fdr();
    cout << "" << endl;
}

string RegressableOperator::get_name() {
    return op->get_name();
}



list<PolicyItem *> perform_regression(const SearchEngine::Plan &plan, vector<pair<int, int> > goal, int distance, bool create_goal) {
    g_timer_regression.resume();
    list<PolicyItem *> reg_steps;
    State *s = new State(*g_initial_state);
        
    vector<State *> states;
    states.push_back(s);
    
    for (int i = 0; i < plan.size(); i++) {
        s = new State(*s, *plan[i]);
        states.push_back(s);
    }
    
    if (g_fullstate) {
            
        if (create_goal) {
            
            State *g = new State();
            
            for (int i = 0; i < goal.size(); i++) {
                (*g)[goal[i].first] = state_var_t(goal[i].second);
            }
        
            reg_steps.push_back(new RegressionStep(g, distance));
            
        } else {
            reg_steps.push_back(new RegressionStep(states.back(), distance));
        }
        
        // Remove the full goal state (we still keep the partial goal state if need be)
        states.pop_back();
        
        for (int i = plan.size() - 1; i >= 0; i--) {
            reg_steps.push_back(new RegressionStep(*plan[i], states.back(), ++distance));
            states.pop_back();
        }
        
        assert(states.empty());
        
    } else {
        
        s = new State();
        
        for (int i = 0; i < goal.size(); i++) {
            (*s)[goal[i].first] = state_var_t(goal[i].second);
        }
    
        reg_steps.push_back(new RegressionStep(s, distance));
        
        for (int i = plan.size() - 1; i >= 0; i--) {
            reg_steps.push_back(new RegressionStep(*plan[i],
                new State(*(reg_steps.back()->state), *plan[i], false, states[i]),
                ++distance));
        }
    }
    
    if (!create_goal) {
        delete reg_steps.front();
        reg_steps.pop_front();
    }
    
    // Strengthen all of the steps so they don't fire a forbidden state-action
    //  pair at some point. The strengthening is sufficient but not neccessary
    s = new State(*g_initial_state);
    State * old_s = s;
    int i = 0;
    for (list<PolicyItem *>::reverse_iterator op_iter = reg_steps.rbegin(); op_iter != reg_steps.rend(); ++op_iter) {
        assert(i < plan.size() || create_goal);
        if (i < plan.size()) {
            ((RegressionStep*)(*op_iter))->strengthen(s);
            s = new State(*old_s, *plan[i], true);
            delete old_s;
            old_s = s;
            i++;
        }
    }
    
    for (int i = 0; i < states.size(); i++)
        delete states[i];
    states.clear();
    
    g_timer_regression.stop();
    return reg_steps;
}

void generate_regressable_ops() {
    list<PolicyItem *> reg_steps;
    list<PolicyItem *> cond_reg_steps;
    
    State *s;
    for (int i = 0; i < g_operators.size(); i++) {
        
        // First, consider operators that lack conditional effects
        if (0 == g_nondet_conditional_mask[g_operators[i].nondet_index]->size()) {
            s = new State();
            
            // Only applicable if the prevail and post conditions currently hold.
            for (int j = 0; j < g_operators[i].get_pre_post().size(); j++) {
                (*s)[g_operators[i].get_pre_post()[j].var] = state_var_t(g_operators[i].get_pre_post()[j].post);
            }
            
            for (int j = 0; j < g_operators[i].get_prevail().size(); j++) {
                (*s)[g_operators[i].get_prevail()[j].var] = state_var_t(g_operators[i].get_prevail()[j].prev);
            }
            
            reg_steps.push_back(new RegressableOperator(g_operators[i], s));
        }
        
        // Next, consider operators that have conditional effects that are consistent
        else {
            s = new State();
            bool consistent = true;
            int var,val;
            
            // Ensure that the conditional effect preconditions are all consistent to fire.
            for (int j = 0; consistent && (j < g_operators[i].get_pre_post().size()); j++) {
                
                var = g_operators[i].get_pre_post()[j].var;
                val = g_operators[i].get_pre_post()[j].pre;
                
                if ((state_var_t(-1) != (*s)[var]) && (state_var_t(val) != (*s)[var])) {
                    consistent = false;
                    break;
                } else {
                    (*s)[var] = state_var_t(val);
                }
                
                for (int k = 0; k < g_operators[i].get_pre_post()[j].cond.size(); k++) {
                    
                    var = g_operators[i].get_pre_post()[j].cond[k].var;
                    val = g_operators[i].get_pre_post()[j].cond[k].prev;
                    
                    if ((state_var_t(-1) != (*s)[var]) && (state_var_t(val) != (*s)[var])) {
                        consistent = false;
                        break;
                    } else {
                        (*s)[var] = state_var_t(val);
                    }
                }
                
            }
            
            for (int j = 0; consistent && (j < g_operators[i].get_prevail().size()); j++) {
                
                var = g_operators[i].get_prevail()[j].var;
                val = g_operators[i].get_prevail()[j].prev;
                
                if ((state_var_t(-1) != (*s)[var]) && (state_var_t(val) != (*s)[var])) {
                    consistent = false;
                    break;
                } else {
                    (*s)[var] = state_var_t(val);
                }
                
            }
            
            
            // Reset the state for checking the post conditions
            delete s;
            s = new State();
            
            
            // Only makes sense to continue if it is consistent so far
            if (consistent) {
                // Only applicable if the prevail and post conditions currently hold.
                for (int j = 0; j < g_operators[i].get_pre_post().size(); j++) {
                    
                    var = g_operators[i].get_pre_post()[j].var;
                    val = g_operators[i].get_pre_post()[j].post;
                    
                    if ((state_var_t(-1) != (*s)[var]) && (state_var_t(val) != (*s)[var])) {
                        consistent = false;
                        break;
                    } else {
                        (*s)[var] = state_var_t(val);
                    }
                    
                }
                
                for (int j = 0; j < g_operators[i].get_prevail().size(); j++) {
                    
                    var = g_operators[i].get_prevail()[j].var;
                    val = g_operators[i].get_prevail()[j].prev;
                    
                    if ((state_var_t(-1) != (*s)[var]) && (state_var_t(val) != (*s)[var])) {
                        consistent = false;
                        break;
                    } else {
                        (*s)[var] = state_var_t(val);
                    }
                    
                }
            }
            
            if (consistent)
                cond_reg_steps.push_back(new RegressableOperator(g_operators[i], s));
            else
                delete s;
        }
    }
    
    g_regressable_ops = new Policy(reg_steps);
    g_regressable_cond_ops = new Policy(cond_reg_steps);
    
}

void RegressionStep::strengthen(State *s) {
    
    if (is_goal)
        return;
    
    vector<PolicyItem *> reg_items;
    g_deadend_policy->generate_applicable_items(*state, reg_items, true);
    
    // Each item could potentially be a forbidden state-action pair
    for (int i = 0; i < reg_items.size(); i++) {
        
        // If this holds, then we may trigger the forbidden pair
        if (((NondetDeadend*)(reg_items[i]))->op_name == op->get_nondet_name()) {
            
            for (int j = 0; j < g_variable_name.size(); j++) {
                // We may have broken it in a previous iteration
                if (((*(((NondetDeadend*)(reg_items[i]))->state))[j] != state_var_t(-1)) &&
                    ((*(((NondetDeadend*)(reg_items[i]))->state))[j] != (*state)[j]) &&
                    ((*state)[j] != state_var_t(-1)))
                    break;
                
                // Just need to break one of the decisions
                if (((*(((NondetDeadend*)(reg_items[i]))->state))[j] != state_var_t(-1)) &&
                    ((*(((NondetDeadend*)(reg_items[i]))->state))[j] != (*s)[j])) {
                    assert((*state)[j] == state_var_t(-1));
                    (*state)[j] = (*s)[j];
                    (*sc_state)[j] = (*s)[j];
                    break;
                    
                }
            }
        }
    }
}

