#include "deadend.h"


bool is_deadend(State &state) {
    ((AdditiveHeuristic *)g_heuristic_for_reachability)->reset();
    return (-1 == ((AdditiveHeuristic *)g_heuristic_for_reachability)->compute_add_and_ff(state));
}


void generalize_deadend(State &state) {
    
    // We disable the pruning of forbidden operators, as we want to be
    //  sure that we have a weak deadend
    bool old_forbidden_val = g_check_with_forbidden;
    g_check_with_forbidden = true;
    
    // If the whole state isn't recognized as a deadend, then don't bother
    //  looking for a subset of the state
    if (!is_deadend(state)) {
        g_check_with_forbidden = old_forbidden_val;
        return;
    }
    
    // We go through each variable and unset it, checking if the relaxed reachability
    //  is violated.
    for (int i = 0; i < g_variable_name.size(); i++) {
        int old_val = state[i];
        state[i] = -1;
        
        // This may help in some scenarios, but it just seems to take uneccessary
        //  time for the current domains.
        //((AdditiveHeuristic *)g_heuristic_for_reachability)->compute_forbidden(state);
        ((AdditiveHeuristic *)g_heuristic_for_reachability)->forbidden_ops.clear(); // Only one of these two lines should be used
        
        // If relaxing variable i causes us to reach the goal, keep it in
        if (!is_deadend(state))
            state[i] = old_val;
    }
    
    g_check_with_forbidden = old_forbidden_val;
    
    //cout << "Found relaxed deadend:" << endl;
    //state.dump();
}

void update_deadends(vector< DeadendTuple* > &failed_states) {
    list<PolicyItem *> de_items;
    list<PolicyItem *> de_states;
    
    State * dummy_state = new State();
    
    for (int i = 0; i < failed_states.size(); i++) {
        
        // Generalize the deadend if need be
        State * failed_state = failed_states[i]->de_state;
        State * failed_state_prev = failed_states[i]->prev_state;
        const Operator * prev_op = failed_states[i]->prev_op;
        
        //cout << "Creating forbidden state-action pairs for deadend:" << endl;
        //failed_state->dump();
        
        // HAZ: Only do the forbidden state-action computation when
        //  the non-deterministic action doesn't have any associated
        //  conditional effects. This is ensured by the construction
        //  of the g_regressable_ops data structure.
        
        // Get the regressable operators for the given state.
        vector<PolicyItem *> reg_items;
        g_regressable_ops->generate_applicable_items(*failed_state, reg_items, true);
        
        // For each operator, create a new deadend avoidance pair
        for (int j = 0; j < reg_items.size(); j++) {
            
            RegressableOperator *ro = (RegressableOperator*)(reg_items[j]);
            
            de_items.push_back(new NondetDeadend(new State(*failed_state, *(ro->op), false, dummy_state),
                                                     ro->op->get_nondet_name()));

            //cout << "Creating new forbidden state-action pair:" << endl;
            //de_items.back()->dump();

            de_states.push_back(new NondetDeadend(new State(*failed_state),
                                                     ro->op->get_nondet_name()));
        }
        
        // If we have a specified previous state and action, use that to
        //  build a forbidden state-action pair
        if (NULL != failed_state_prev) {
            de_items.push_back(new NondetDeadend(
                    new State(*failed_state, *prev_op, false, failed_state_prev),
                    prev_op->get_nondet_name()));
            
            de_states.push_back(new NondetDeadend(new State(*failed_state),
                                                  prev_op->get_nondet_name()));
            
        }
    }
    
    delete dummy_state;
    
    g_deadend_policy->update_policy(de_items);
    g_deadend_states->update_policy(de_states);
}


void DeadendAwareSuccessorGenerator::generate_applicable_ops(const State &curr, vector<const Operator *> &ops) {
    if (g_detect_deadends && g_deadend_policy) {
        
        vector<PolicyItem *> reg_items;
        vector<const Operator *> orig_ops;
        
        g_successor_generator_orig->generate_applicable_ops(curr, orig_ops);
        g_deadend_policy->generate_applicable_items(curr, reg_items);
        
        set<int> forbidden;
        for (int i = 0; i < reg_items.size(); i++)
            forbidden.insert(g_nondet_index_mapping[((NondetDeadend*)(reg_items[i]))->op_name]);
        
        for (int i = 0; i < orig_ops.size(); i++) {
            if (0 == forbidden.count(orig_ops[i]->nondet_index)) {
                //cout << "Allowing operator " << orig_ops[i]->get_name() << endl;
                ops.push_back(orig_ops[i]);
            }
            else {
                /* HAZ: Since we are using the ff heuristic with preferred operators,
                 *      we don't want the preferred operators to sneak into the applicable
                 *      list of actions. As such, we "mark" the operator which prevents
                 *      the operator from being added. See LazySearch::get_successor_operators
                 *      for where this occurrs.
                 */
                orig_ops[i]->mark();
                
                //cout << "Forbidding operator " << orig_ops[i]->get_name() << endl;
            }
        }
        
        // Add this state as a deadend if we have ruled out everything
        //if (ops.empty()) {
        //    cout << "Adding a new deadend state..." << endl;
        //    vector<State *> failed_states;
        //    failed_states.push_back(new State(curr));
        //    update_deadends(failed_states);
        //}
        
    } else {
        
        g_successor_generator_orig->generate_applicable_ops(curr, ops);
        
    }
    return;
}
