#include "jit.h"

void UnhandledState::dump() const {
    cout << "Unhandled State of distance " << cost << ":" << endl;
    state->dump();
}


void perform_jit_repairs(SearchEngine *engine, int argc, const char **argv, float){ // Note: Currently we aren't using the time bound
    set<UnhandledState> open_states;
    Simulator *sim = new Simulator(engine, argc, argv, true);
    
    find_unhandled_states(g_initial_state, engine->get_plan(), open_states, 0);
    
    while (open_states.size() > 0) { // Should also check for time
        UnhandledState current_state = *(open_states.begin());
        
        cout << "Open states left: " << open_states.size() << endl;
        cout << "Handling a new open state of distance " << current_state.cost << endl;
        
        if (!current_state.state)
            cout << "Uh oh!" << endl;
        sim->set_state(current_state.state);
        sim->replan();
        
        if (!current_state.state)
            cout << "Uh oh! (v2)" << endl;
        find_unhandled_states(current_state.state, sim->get_engine()->get_plan(), open_states, current_state.cost);
        
        if (!current_state.state)
            cout << "Uh oh! (v3)" << endl;
        open_states.erase(open_states.begin());
    }
    cout << "Done Repairing!!!" << endl;
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
