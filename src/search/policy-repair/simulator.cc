#include "simulator.h"

Simulator::Simulator(Policy *pol, SearchEngine *eng) : policy(pol), engine(eng) {
    current_state = new State(*g_initial_state);
}

void Simulator::run() {
    bool going = true;
    vector<RegressionStep *> current_steps;
    
    while(going) {
        // Get the applicable options
        current_steps.clear();
        policy->generate_applicable_steps(*current_state, current_steps);
        
        // Check for failure
        if (0 == current_steps.size()) {
            failed_states++;
            replan();
        } else {
            successful_states++;
            int best_index = 0;
            int best_val = current_steps[0]->distance;
            bool found_goal = false;
            
            for (int i = 0; i < current_steps.size(); i++) {
                if (current_steps[i]->is_goal) {
                    found_goal = true;
                    break;
                }
                
                if (current_steps[i]->distance < best_val) {
                    best_val = current_steps[i]->distance;
                    best_index = i;
                }
            }
            
            if (found_goal) {
                cout << "...achieved the goal!" << endl;
                going = false;
            } else {
                // Execute the non-deterministic action
                execute_action(current_steps[best_val]->op);
            }
        }
        
    }
}

void Simulator::execute_action(const Operator *op) {
    // Choose the op
    Operator *chosen = g_nondet_mapping[op->get_nondet_name()][rand() % g_nondet_mapping[op->get_nondet_name()].size()];
    State *old_state = current_state;
    current_state = new State(*old_state, *chosen);
    delete old_state;
}

void Simulator::replan() {
    engine->search();
}

void Simulator::dump() {
    cout << "-{ Simulator Statistics }-" << endl;
    cout << "Successful states: " << successful_states << endl;
    cout << "Replans: " << failed_states << endl;
    cout << "Actions: " << (successful_states + failed_states) << endl;
}
