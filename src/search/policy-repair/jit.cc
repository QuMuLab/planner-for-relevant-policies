#include "jit.h"

void UnhandledState::dump() const {
    cout << "Unhandled State of distance " << cost << ":" << endl;
    state->dump();
}


bool perform_jit_repairs(Simulator *sim) { // Note: Currently we aren't using the time bound
    queue<State *> open_list;
    set<State> seen;
    State *current_state;
    bool made_change = false;
    
    State *old_initial_state = new State(*g_initial_state);
    
    open_list.push(new State(*g_initial_state));
    
    while (!open_list.empty() && (g_timer_jit() < g_jic_limit)) {
        current_state = open_list.front();
        open_list.pop();
        
        if (0 == seen.count(*current_state)) {
            seen.insert(*current_state);
        
            // See if we can handle this state
            RegressionStep * regstep = g_policy->get_best_step(*current_state);
            bool have_solution = true;
            
            if (0 == regstep) {
                sim->set_state(current_state);
                have_solution = sim->replan();
                
                if (have_solution) {
                    regstep = g_policy->get_best_step(*current_state);
                    made_change = true;
                }
            }
            
            if (have_solution) {
                assert(regstep);
                
                if (!(regstep->is_goal)) {
                    //cout << "Searching through operator " << regstep->op->get_nondet_name() << endl;
                    for (int i = 0; i < g_nondet_mapping[regstep->op->get_nondet_name()].size(); i++) {
                        State *new_state = new State(*current_state, *(g_nondet_mapping[regstep->op->get_nondet_name()][i]));
                        if (0 == seen.count(*new_state))
                            open_list.push(new_state);
                    }
                }
            } else {
                g_failed_open_states++;
            }
        }
    }
    
    if (!g_silent_planning)
        cout << "Could not close " << g_failed_open_states << " open leaf states." << endl;
    g_initial_state = old_initial_state;
    sim->set_state(g_initial_state);
    return made_change;
}

void perform_jit_repairs_old(SearchEngine *engine, int argc, const char **argv){ // Note: Currently we aren't using the time bound
    set<UnhandledState> open_states;
    Simulator *sim = new Simulator(engine, argc, argv, true);
    State *old_initial_state = new State(*g_initial_state);
    
    find_unhandled_states(g_initial_state, engine->get_plan(), open_states, 0);
    
    while (open_states.size() > 0) { // Should also check for time
        UnhandledState current_state = *(open_states.begin());
        
        cout << "Open states left: " << open_states.size() << endl;
        
        if (g_policy->get_best_step(*(current_state.state)) == 0) {
            
            cout << "Handling a new open state of distance " << current_state.cost << endl;
        
            sim->set_state(current_state.state);
            sim->replan();
        
            find_unhandled_states(current_state.state, sim->get_engine()->get_plan(), open_states, current_state.cost);
        
        } else {
            cout << "Found a leaf already closed of distance " << current_state.cost << endl;
        }
        
        open_states.erase(open_states.begin());
        
    }
    g_initial_state = old_initial_state;
    cout << "Finished repair round." << endl;
}

void find_unhandled_states(State *state, const SearchEngine::Plan &plan, set<UnhandledState> &unhandled, int cost) {
    State *current_state = new State(*state);
    int cur_cost = cost + 1;
    for (int i = 0; i < plan.size(); i++) {
        for (int j = 0; j < g_nondet_mapping[plan[i]->get_nondet_name()].size(); j++) {
            State *new_state = new State(*current_state, *(g_nondet_mapping[plan[i]->get_nondet_name()][j]));
            if (g_policy->get_best_step(*new_state)) {
                delete new_state;
            } else {
                cout << "Adding new open state of distance " << cur_cost << endl;
                unhandled.insert(UnhandledState(new_state, cur_cost));
            }
        }
        cur_cost++;
        State *old_state = current_state;
        current_state = new State(*old_state, *(plan[i]));
        delete old_state;
    }
}
