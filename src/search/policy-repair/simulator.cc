#include "simulator.h"
#include "../option_parser.h"

Simulator::Simulator(SearchEngine *eng, int _argc, const char **_argv, bool verb) :
                    engine(eng), argc(_argc), argv(_argv), verbose(verb), found_solution(false) {
    current_state = new State(*g_initial_state);
    successful_states = 0;
    failed_states = 0;
}

void Simulator::run() {
    RegressionStep * current_step;
    
    while(!found_solution) {
        // Get the best action (if any)
        current_step = g_policy->get_best_step(*current_state);
        
        if (current_step) {
            
            successful_states++;
            
            if (current_step->is_goal) {
                cout << "...achieved the goal!" << endl;
                found_solution = true;
            } else {
                // Execute the non-deterministic action
                execute_action(current_step->op);
            }
        } else {
            failed_states++;
            replan();
        }
    }
}

void Simulator::execute_action(const Operator *op) {
    
    if (verbose) {
        cout << "\nExpected operator:" << endl << "  ";
        op->dump();
    }
    
    // Choose the op
    Operator *chosen = g_nondet_mapping[op->get_nondet_name()][rand() % g_nondet_mapping[op->get_nondet_name()].size()];
    
    if (verbose) {
        cout << "Chosen operator:" << endl << "  ";
        chosen->dump();
    }
    
    State *old_state = current_state;
    current_state = new State(*old_state, *chosen);
    delete old_state;
}

void Simulator::replan() {
    if (verbose)
        cout << "\nRequired to replan..." << endl;

    if (engine)
        delete engine;
    if (g_initial_state)
        delete g_initial_state;
    
    if (verbose)
        cout << "Creating initial state." << endl;
    if (!current_state) {
        cout << "Error: No current state for the replan." << endl;
        exit(0);
    }
    g_initial_state = new State(*current_state);
    
    if (verbose)
        cout << "Creating new engine." << endl;
    engine = OptionParser::parse_cmd_line(argc, argv, false);
    
    if (verbose)
        cout << "Searching for a solution." << endl;
    engine->search();
    
    if (verbose)
        cout << "Building the regression list." << endl;
    list<RegressionStep *> regression_steps = perform_regression(engine->get_plan(), g_matched_policy, g_matched_distance);
    
    if (verbose)
        cout << "Updating the policy." << endl;
    g_policy->update_policy(regression_steps);
}

void Simulator::dump() {
    cout << "-{ Simulator Statistics }-" << endl;
    cout << "Successful states: " << successful_states << endl;
    cout << "Replans: " << failed_states << endl;
    cout << "Actions: " << (successful_states + failed_states) << endl;
}
