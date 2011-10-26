#include "jit.h"

void UnhandledState::dump() const {
    cout << "Unhandled State of distance " << cost << ":" << endl;
    state->dump();
}


bool perform_jit_repairs(Simulator *sim) {
    queue<pair<State *, State *> > open_list;
    set<State> seen;
    State *current_state;
    State *current_goal;
    bool made_change = false;
    
    State *old_initial_state = new State(*g_initial_state);
    
    // Build the goal state
    State *goal_orig = new State(*g_initial_state);
    for (int i = 0; i < g_variable_name.size(); i++) {
        (*goal_orig)[i] = state_var_t(-1);
    }
    for (int i = 0; i < g_goal.size(); i++) {
        (*goal_orig)[g_goal[i].first] = state_var_t(g_goal[i].second);
    }
    
    open_list.push(make_pair(new State(*g_initial_state), new State(*goal_orig)));
    
    while (!open_list.empty() && (g_timer_jit() < g_jic_limit)) {
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
                    
                    for (int i = 0; i < g_nondet_mapping[regstep->op->get_nondet_name()].size(); i++) {
                        State *new_state = new State(*current_state, *(g_nondet_mapping[regstep->op->get_nondet_name()][i]));
                        if (0 == seen.count(*new_state))
                            open_list.push(make_pair(new_state, expected_state));
                    }
                }
                
            } else {
                g_failed_open_states++;
            }
        }
        //delete current_state;
        //delete current_goal; // Current_goal goes into many tuples -- memory leak here
    }
    
    if (!g_silent_planning)
        cout << "Could not close " << g_failed_open_states << " open leaf states." << endl;
    g_initial_state = old_initial_state;
    sim->set_state(g_initial_state);
    sim->set_goal(goal_orig);
    return made_change;
}
