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
    state->dump_pddl();
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
    state->dump_pddl();
    cout << "" << endl;
}

string RegressableOperator::get_name() {
    return op->get_name();
}



list<PolicyItem *> perform_regression(const SearchEngine::Plan &plan, vector<pair<int, int> > goal, int distance, bool create_goal) {
    g_timer_regression.resume();
    list<PolicyItem *> reg_steps;
    PartialState *s = new PartialState(g_initial_state());
    
    if (g_fullstate) {
        
        vector<PartialState *> states;
        states.push_back(s);
        
        for (int i = 0; i < plan.size(); i++) {
            s = new PartialState(*s, *plan[i]);
            states.push_back(s);
        }
        
        if (create_goal) {
            
            PartialState *g = new PartialState();
            
            for (int i = 0; i < goal.size(); i++) {
                (*g)[goal[i].first] = int(goal[i].second);
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
		s = new PartialState();
        
        for (int i = 0; i < goal.size(); i++) {
            (*s)[goal[i].first] = int(goal[i].second);
        }
    
        reg_steps.push_back(new RegressionStep(s, distance));
        
        for (int i = plan.size() - 1; i >= 0; i--) {
            reg_steps.push_back(new RegressionStep(*plan[i], new PartialState(*(reg_steps.back()->state), *plan[i], false), ++distance));
        }
    }
    
    if (!create_goal) {
        delete reg_steps.front();
        reg_steps.pop_front();
    }
    
    // Strengthen all of the steps so they don't fire a forbidden state-action
    //  pair at some point. The strengthening is sufficient but not neccessary
    s = new PartialState(g_initial_state());
    PartialState * old_s = s;
    int i = 0;
    for (list<PolicyItem *>::reverse_iterator op_iter = reg_steps.rbegin(); op_iter != reg_steps.rend(); ++op_iter) {
        assert(i < plan.size() || create_goal);
        if (i < plan.size()) {
            ((RegressionStep*)(*op_iter))->strengthen(s);
            s = new PartialState(*old_s, *plan[i], true);
            delete old_s;
            old_s = s;
            i++;
        }
    }
    
    g_timer_regression.stop();
    return reg_steps;
}

void generate_regressable_ops() {
    list<PolicyItem *> reg_steps;
    PartialState *s;
    for (int i = 0; i < g_operators.size(); i++) {
        s = new PartialState();
        // Only applicable if the prevail and post conditions currently hold.
        for (int j = 0; j < g_operators[i].get_pre_post().size(); j++) {
            (*s)[g_operators[i].get_pre_post()[j].var] = g_operators[i].get_pre_post()[j].post;
        }
        
        for (int j = 0; j < g_operators[i].get_prevail().size(); j++) {
            (*s)[g_operators[i].get_prevail()[j].var] = g_operators[i].get_prevail()[j].prev;
        }
        
        reg_steps.push_back(new RegressableOperator(g_operators[i], s));
    }
    g_regressable_ops = new Policy();
    g_regressable_ops->update_policy(reg_steps);
}

void RegressionStep::strengthen(PartialState *s) {
    
    if (is_goal)
        return;
    
    vector<PolicyItem *> reg_items;
    g_deadend_policy->generate_applicable_items(*state, reg_items, true);
    
    // Each item could potentially be a forbidden state-action pair
    for (int i = 0; i < reg_items.size(); i++) {
        
        // If this holds, then we may trigger the forbidden pair
        if (((NondetDeadend*)(reg_items[i]))->op_name == op->get_nondet_name()) {
            
            for (int j = 0; j < g_variable_name.size(); j++) {
                
                int val = (*(((NondetDeadend*)(reg_items[i]))->state))[j];
                
                // We may have broken it in a previous iteration
                if ((val != -1) &&
                    (val != (*state)[j]) &&
                    ((*state)[j] != -1))
                        break;
                
                // Just need to break one of the decisions
                if ((val != -1) &&
                    (val != (*s)[j])) {
                    
                    assert((*state)[j] == -1);
                    (*state)[j] = (*s)[j];
                    break;
                    
                }
            }
        }
    }
}

