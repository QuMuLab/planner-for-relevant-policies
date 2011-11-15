#include "jit.h"

void UnhandledState::dump() const {
    cout << "Unhandled State of distance " << cost << ":" << endl;
    state->dump();
}


bool perform_jit_repairs(Simulator *sim) {
    queue<pair<State *, State *> > open_list;
    set<State> seen;
    vector<State *> created_states;
    State *current_state;
    State *current_goal;
    bool made_change = false;
    g_failed_open_states = 0;
    int num_checked_states = 0;
    vector<State *> failed_states;
    
    State *old_initial_state = new State(*g_initial_state);
    
    // Build the goal state
    State *goal_orig = new State();
    for (int i = 0; i < g_goal.size(); i++) {
        (*goal_orig)[g_goal[i].first] = state_var_t(g_goal[i].second);
    }
    
    current_state = new State(*g_initial_state);
    current_goal = new State(*goal_orig);
    open_list.push(make_pair(current_state, current_goal));
    
    created_states.push_back(current_state);
    created_states.push_back(current_goal);
    
    while (!open_list.empty() && (g_timer_jit() < g_jic_limit)) {
        num_checked_states++;
        current_state = open_list.front().first;
        current_goal = open_list.front().second;
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
                
                if (have_solution) {
                    regstep = g_policy->get_best_step(*current_state);
                    made_change = true;
                }
            }
            
            if (have_solution) {
                
                assert(regstep);
                
                if (!(regstep->is_goal)) {
                    // Record the expected state
                    State *expected_state = new State(*current_state, *(regstep->op));
                    created_states.push_back(expected_state);
                    
                    for (int i = 0; i < g_nondet_mapping[regstep->op->get_nondet_name()].size(); i++) {
                        State *new_state = new State(*current_state, *(g_nondet_mapping[regstep->op->get_nondet_name()][i]));
                        created_states.push_back(new_state);
                        if (0 == seen.count(*new_state))
                            open_list.push(make_pair(new_state, expected_state));
                    }
                }
                
            } else {
                if (g_detect_deadends)
                    failed_states.push_back(current_state);
                g_failed_open_states++;
                
                // This only matches when no strong cyclic solution exists
                if (*current_state == *old_initial_state) {
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
                    g_policy->mark_complete();
                    
                    // Clean up the states we've created
                    for (int i = 0; i < created_states.size(); i++) {
                        if (created_states[i])
                            delete created_states[i];
                    }
                    
                    // Return false so jic stops
                    return false;
                }
            }
        }
    }
    
    g_initial_state = old_initial_state;
    sim->set_state(g_initial_state);
    sim->set_goal(goal_orig);
    
    //if (!g_silent_planning) {
        cout << "\nCould not close " << g_failed_open_states << " open leaf states." << endl;
        cout << "Investigated " << num_checked_states << " states for the strong cyclic plan." << endl;
    //}
        
    if (0 == g_failed_open_states)
        g_policy->mark_strong();
        
    if (g_detect_deadends && (g_failed_open_states > 0)) {
        
        update_deadends(failed_states);
        
        double cur_score = g_policy->get_score();
        if (cur_score > g_best_policy_score) {
            
            //if (!g_silent_planning)
                cout << "Found a better policy of score " << cur_score << endl;
            
            if (g_best_policy && (g_best_policy != g_policy))
                delete g_best_policy;
            
            g_best_policy_score = cur_score;
            g_best_policy = g_policy;
            
        } else {
            
            //if (!g_silent_planning)
                cout << "Went through another policy of score " << cur_score << endl;
            if (g_best_policy != g_policy)
                delete g_policy;
        }
        
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
