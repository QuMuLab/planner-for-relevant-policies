#include "jit.h"

void UnhandledState::dump() const {
    cout << "Unhandled State of distance " << cost << ":" << endl;
    state->dump();
}


struct SCNode {
    State * full_state;
    State * expected_state;
    State * previous_state;
    RegressionStep * prev_regstep;
    const Operator * prev_op;
    SCNode(State * fs, State * es, State * ps, RegressionStep * pr, const Operator * op) :
       full_state(fs), expected_state(es), previous_state(ps), prev_regstep(pr), prev_op(op) {}
};

bool perform_jit_repairs(Simulator *sim) {
    // The use of a stack is important for efficiency when using the optimized_scd.
    //  We close states closer to the end in the hope that strong cyclic reasoning
    //  will allow us to cease traversing the state space earlier, with a guarantee
    //  from the partial policy of partial states that a strong cyclic solution still
    //  exists.
    stack<SCNode> open_list; // Open list we traverse until strong cyclicity is proven
    set<State> seen; // Keeps track of the full states we've seen
    vector<State *> created_states; // Used to clean up the created state objects
    State * current_state; // The current step in the loop
    State * previous_state; // The previous step in the loop (leading to the current_state)
    State * current_goal; // The current goal in the loop
    const Operator * prev_op; // The last operator used to get us to current_state
    RegressionStep * prev_regstep; // The last RegressionStep that triggered prev_op
    bool made_change = false; // True if we add anything to the g_policy (i.e., replan)
    g_failed_open_states = 0; // Number of open states we couldn't solve (i.e., deadends)
    int num_checked_states = 0; // Number of states we check
    int num_fixed_states = 0; // Number of states we were able to repair (by replanning)
    vector< DeadendTuple * > failed_states; // The failed states (used for creating deadends)
    
    // In case we have an initial policy, we run the optimized scd.
    if (g_optimized_scd) {
        g_policy->init_scd();
        made_change = true; // This becomes false again eventually
        while (made_change)
            made_change = g_policy->step_scd(failed_states);
    }
    
    // Back up the originial initial state
    State *old_initial_state = new State(*g_initial_state);
    
    // Build the goal state
    State *goal_orig = new State();
    for (int i = 0; i < g_goal.size(); i++) {
        (*goal_orig)[g_goal[i].first] = state_var_t(g_goal[i].second);
    }
    
    current_state = new State(*g_initial_state);
    current_goal = new State(*goal_orig);
    open_list.push(SCNode(current_state, current_goal, NULL, NULL, NULL));
    
    created_states.push_back(current_state);
    created_states.push_back(current_goal);
    
    while (!open_list.empty() && (g_timer_jit() < g_jic_limit)) {
        num_checked_states++;
        current_state = open_list.top().full_state;
        previous_state = open_list.top().previous_state;
        current_goal = open_list.top().expected_state;
        prev_regstep = open_list.top().prev_regstep;
        prev_op = open_list.top().prev_op;
        open_list.pop();
        
        if (0 == seen.count(*current_state)) {
            
            seen.insert(*current_state);
        
            // See if we can handle this state
            RegressionStep * regstep = g_policy->get_best_step(*current_state);
            
            bool have_solution = true;
            
            if (0 == regstep) {
            
                sim->set_state(current_state);
                sim->set_goal(current_goal);
                have_solution = sim->replan();
                
                // It may happen that solving creates a bad policy, and a second pass catches this
                if (!(g_policy->get_best_step(*current_state)))
                    have_solution = sim->replan();
                
                
                // Add the new goals to the sc condition for the previous reg step
                if (g_optimized_scd && prev_regstep && have_solution) {
                    
                    // regstep is now at the start of the newly found plan
                    regstep = g_policy->get_best_step(*current_state);
                    
                    // prev_state holds the info needed before the operator was taken
                    State * prev_state = new State(*(regstep->state), *prev_op, false, prev_regstep->sc_state);
                    
                    // We augment the sc_state to include the stronger conditions
                    for (int i = 0; i < g_variable_name.size(); i++) {
                        /*assert ((state_var_t(-1) == (*prev_state)[i]) ||
                                (state_var_t(-1) == (*(prev_regstep->sc_state))[i]) ||
                               ((*prev_state)[i] == (*(prev_regstep->sc_state))[i]));*/
                        
                        if (state_var_t(-1) != (*prev_state)[i])
                            (*(prev_regstep->sc_state))[i] = (*prev_state)[i];
                    }
                }
                
                // Since new policy has been added, we re-compute the sc detection
                if (g_optimized_scd && have_solution) {
                    g_policy->init_scd();
                    bool _made_change = true;
                    while (_made_change)
                        _made_change = g_policy->step_scd(failed_states);
                }
                
                if (have_solution) {
                    num_fixed_states++;
                    // We recompute the regstep here, just in case we need a better
                    //  strong cyclic one after the sc detection occurs.
                    regstep = g_policy->get_best_step(*current_state);
                    made_change = true;
                }
            }
            
            if (have_solution) {
                
                assert(regstep);
                
                if ( ! (regstep->is_goal || (g_optimized_scd && regstep->is_sc))) {
                    // Record the expected state
                    State *full_expected_state = new State(*current_state, *(regstep->op));
                    State *expected_state = full_expected_state;
                    created_states.push_back(full_expected_state);
                    
                    if (g_partial_planlocal) {
                        RegressionStep * expected_regstep = g_policy->get_best_step(*full_expected_state);
                        if (expected_regstep) {
                            expected_state = new State(*(expected_regstep->state));
                            created_states.push_back(expected_state);
                        }
                    }
                    
                    for (int i = 0; i < g_nondet_mapping[regstep->op->nondet_index]->size(); i++) {
                        State *new_state = new State(*current_state, *((*(g_nondet_mapping[regstep->op->nondet_index]))[i]));
                        created_states.push_back(new_state);
                        if (0 == seen.count(*new_state))
                            open_list.push(SCNode(new_state, expected_state, current_state, regstep, (*(g_nondet_mapping[regstep->op->nondet_index]))[i]));
                    }
                    // We add this one extra time to ensure a DFS traversal of the
                    //  state space when looking for a strong cyclic solution. This
                    //  introduces a duplicate, but the outer if statement catches
                    //  this just fine, and the memory hit is negligible.
                    open_list.push(SCNode(full_expected_state, expected_state, current_state, regstep, regstep->op));
                }
                
            } else {

                g_failed_open_states++;
                
                // This only matches when no strong cyclic solution exists
                if (*current_state == *old_initial_state) {
                    if (g_detect_deadends)
                        g_failed_open_states = failed_states.size();
                    
                    if (!g_silent_planning) {
                        cout << "Found the initial state to be a failed one. No strong cyclic plan exists." << endl;
                        cout << "Using the best policy found, with a score of " << g_best_policy_score << endl;
                    }
                    g_initial_state = old_initial_state;
                    sim->set_state(g_initial_state);
                    sim->set_goal(goal_orig);
                    
                    // Use the best policy we've found so far
                    if (g_best_policy != g_policy)
                        delete g_policy;
                    g_policy = g_best_policy;

                    if (g_timer_jit() < g_jic_limit)
                        g_policy->mark_complete();
                    
                    // Clean up the states we've created
                    for (int i = 0; i < created_states.size(); i++) {
                        if (created_states[i])
                            delete created_states[i];
                    }
                    
                    // Return false so jic stops
                    return false;
                } else {
                    if (g_detect_deadends) {
                        if (g_generalize_deadends)
                            generalize_deadend(*current_state);
                        failed_states.push_back(new DeadendTuple(current_state, previous_state, prev_op));
                    }
                }
            }
        }
    }
    
    // We need to update the value since some may have been added to the
    //  list during optimized_scd
    if (g_detect_deadends)
        g_failed_open_states = failed_states.size();
    
    // Reset the original goal and initial state
    g_initial_state = old_initial_state;
    sim->set_state(g_initial_state);
    sim->set_goal(goal_orig);
    
    cout << "\nCould not close " << g_failed_open_states << " of " << num_fixed_states + g_failed_open_states << " open leaf states." << endl;
    cout << "Investigated " << num_checked_states << " states for the strong cyclic plan." << endl;
    
    // If we closed every open state, then the policy must be strongly cyclic.
    if ((0 == g_failed_open_states) && (g_timer_jit() < g_jic_limit))
        g_policy->mark_strong();
        
    if (g_detect_deadends && (g_failed_open_states > 0)) {
        
        update_deadends(failed_states);
        
        double cur_score = g_policy->get_score();
        if (cur_score > g_best_policy_score) {
            
            cout << "Found a better policy of score " << cur_score << endl;
            
            if (g_best_policy && (g_best_policy != g_policy))
                delete g_best_policy;
            
            g_best_policy_score = cur_score;
            g_best_policy = g_policy;
            
        } else {
            
            cout << "Went through another policy of score " << cur_score << endl;
            if (g_best_policy != g_policy)
                delete g_policy;
        }
        
        // We delete the policy so we can start from scratch next time with
        //  the deadends recorded.
        g_policy = new Policy();
        
        made_change = true;
    }
    
    // Clean up the states we've created
    for (int i = 0; i < created_states.size(); i++) {
        if (created_states[i])
            delete created_states[i];
    }
    
    return made_change;
}
