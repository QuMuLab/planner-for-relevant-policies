#include "simulator.h"
#include "../option_parser.h"

Simulator::Simulator(SearchEngine *eng, int _argc, const char **_argv, bool verb) :
                    engine(eng), argc(_argc), argv(_argv), verbose(verb), succeeded(false), found_solution(false) {
    current_state = new State(*g_initial_state);
    successful_states = 0;
    failed_states = 0;
    record_succeeded = 0;
}

void Simulator::run() {
    for (int i = 0; i < g_num_trials; i++) {
        run_once();
        record_stats();
    }
}

void Simulator::record_stats() {
    record_successful_states.push_back(successful_states);
    record_failed_states.push_back(failed_states);
    record_total_states.push_back(successful_states + failed_states);
    if (succeeded)
        record_succeeded++;
}

void Simulator::run_once() {
    found_solution = false;
    succeeded = false;
    RegressionStep * current_step;
    successful_states = 0;
    failed_states = 0;
    
    State *orig_init_state = new State(*g_initial_state);
    current_state = new State(*g_initial_state);
    
    reset_goal();
    
    
    while(!found_solution) {
        // Get the best action (if any)
        current_step = g_policy->get_best_step(*current_state);
        
        if (current_step) {
            
            successful_states++;
            
            if (current_step->is_goal) {
                if (verbose || (1 == g_num_trials))
                    cout << "...achieved the goal!" << endl;
                succeeded = true;
                found_solution = true;
            } else {
                // Execute the non-deterministic action
                execute_action(current_step->op);
            }
            
        } else {
            failed_states++;
            if (!replan()) {
                if (verbose || (1 == g_num_trials))
                    cout << "Got into a dead-end state..." << endl;
                found_solution = true;
            }
        }
    }
    
    g_initial_state = orig_init_state;
}

bool Simulator::execute_action(const Operator *op) {
    
    if (verbose) {
        cout << "\nExpected operator:" << endl << "  ";
        op->dump();
    }
    
    // Choose the op
    int choice = g_rng.next(g_nondet_mapping[op->get_nondet_name()].size());
    Operator *chosen = g_nondet_mapping[op->get_nondet_name()][choice];
    
    if (verbose) {
        cout << "Chosen operator:" << endl << "  ";
        chosen->dump();
    }
    
    State *old_state = current_state;
    current_state = new State(*old_state, *chosen);
    delete old_state;
    
    return (op->get_name() == chosen->get_name());
}

void Simulator::reset_goal() {
    g_goal.clear();
    for (int i = 0; i < g_goal_orig.size(); i++)
        g_goal.push_back(make_pair(g_goal_orig[i].first, g_goal_orig[i].second));
}

bool Simulator::replan() {
    if (verbose)
        cout << "\nRequired to replan..." << endl;

    if (engine)
        delete engine;
    if (g_initial_state)
        delete g_initial_state;
    
    if (!current_state) {
        cout << "Error: No current state for the replan." << endl;
        exit(0);
    }
    
    if (verbose)
        cout << "Creating initial state." << endl;
    g_initial_state = new State(*current_state);
    
    if (g_plan_locally) {
        if (verbose)
            cout << "Resetting the goal state." << endl;
        
        g_goal.clear();
        for (int i = 0; i < g_variable_name.size(); i++) {
            if ((*current_goal)[i] != state_var_t(-1))
                g_goal.push_back(make_pair(i, (*current_goal)[i]));
        }
    }
    
    if (verbose)
        cout << "Creating new engine." << endl;
    bool engine_ready = true;
    g_timer_engine_init.resume();
    try {
        engine = OptionParser::parse_cmd_line(argc, argv, false);
    } catch (SolvableError &se) {
        if (!g_silent_planning)
            cout << se;
        engine = 0; // Memory leak seems necessary --> engine can't be deleted.
        engine_ready = false;
    }
    g_timer_engine_init.stop();
    
    bool try_again = g_plan_locally; // Will hold later only if the engine was created, and no plan works, and we want to plan locally
    
    if (!engine_ready && g_plan_locally) {
        try_again = false;
        if (verbose)
            cout << "Failed to create the engine for the new goal." << endl;
        
        reset_goal();
        
        if (verbose)
            cout << "Creating new engine." << endl;
        engine_ready = true;
        g_timer_engine_init.resume();
        try {
            engine = OptionParser::parse_cmd_line(argc, argv, false);
        } catch (SolvableError &se) {
            if (!g_silent_planning)
                cout << se;
            engine = 0; // Memory leak seems necessary --> engine can't be deleted.
            engine_ready = false;
        }
        g_timer_engine_init.stop();
    }
    
    if (engine_ready) {
        if (verbose)
            cout << "Searching for a solution." << endl;
        g_timer_search.resume();
        engine->search();
        g_timer_search.stop();
        
        if (engine->found_solution()) {
            
            if (verbose)
                cout << "Building the regression list." << endl;
            list<RegressionStep *> regression_steps = perform_regression(engine->get_plan(), g_matched_policy, g_matched_distance);
            
            if (verbose)
                cout << "Updating the policy." << endl;
            g_policy->update_policy(regression_steps);
            
            reset_goal();
            return true;
            
        } else {
            
            reset_goal();
            
            if (try_again) {
                delete engine;
                
                if (verbose)
                    cout << "Creating new engine." << endl;
                g_timer_engine_init.resume();
                try {
                    engine = OptionParser::parse_cmd_line(argc, argv, false);
                } catch (SolvableError &se) {
                    if (!g_silent_planning)
                        cout << se;
                    engine = 0; // Memory leak seems necessary --> engine can't be deleted.
                    if (verbose)
                        cout << "Replanning failed!" << endl;
                    g_timer_engine_init.stop();
                    return false;
                }
                g_timer_engine_init.stop();
                
                if (verbose)
                    cout << "Searching for a solution." << endl;
                g_timer_search.resume();
                engine->search();
                g_timer_search.stop();
                
                if (engine->found_solution()) {
                    if (verbose)
                        cout << "Building the regression list." << endl;
                    list<RegressionStep *> regression_steps = perform_regression(engine->get_plan(), g_matched_policy, g_matched_distance);
                    
                    if (verbose)
                        cout << "Updating the policy." << endl;
                    g_policy->update_policy(regression_steps);
                    
                    return true;
                }
            }
            if (verbose)
                cout << "Replanning failed!" << endl;
            return false;
        }
    } else {
        if (verbose)
            cout << "Replanning failed!" << endl;
        reset_goal();
        return false;
    }
}

void Simulator::run_ffreplan(queue<const Operator *> &plan) {
    
    reset_goal();
    
    successful_states = 0;
    failed_states = 0;
    
    while(!test_goal(*current_state)) {
        
        const Operator *op = plan.front();
        plan.pop();
        
        if (execute_action(op)) {
            successful_states++;
        } else {
            failed_states++;
            if (verbose)
                cout << "\nRequired to replan..." << endl;

            if (engine)
                delete engine;
            if (g_initial_state)
                delete g_initial_state;
            
            if (!current_state) {
                cout << "Error: No current state for the replan." << endl;
                exit(0);
            }
            
            if (verbose)
                cout << "Creating initial state." << endl;
            g_initial_state = new State(*current_state);
            
            if (verbose)
                cout << "Creating new engine." << endl;
            bool engine_ready = true;
            g_timer_engine_init.resume();
            try {
                engine = OptionParser::parse_cmd_line(argc, argv, false);
            } catch (SolvableError &se) {
                if (!g_silent_planning)
                    cout << se;
                engine = 0; // Memory leak seems necessary --> engine can't be deleted.
                engine_ready = false;
            }
            g_timer_engine_init.stop();
            
            if (engine_ready) {
                if (verbose)
                    cout << "Searching for a solution." << endl;
                g_timer_search.resume();
                engine->search();
                g_timer_search.stop();
                
                if (engine->found_solution()) {
                    if (verbose)
                        cout << "Replanning succeeded." << endl;
                    
                    plan = queue<const Operator *>();
                    
                    for (int i = 0; i < engine->get_plan().size(); i++)
                        plan.push(engine->get_plan()[i]);
                    
                } else {
                    cout << "Replanning failed!" << endl;
                    succeeded = false;
                    return;
                }
            } else {
                cout << "Replanning failed!" << endl;
                succeeded = false;
                return;
            }
        }
    }
    cout << "...achieved the goal!" << endl;
    succeeded = true;
}

float average(vector<int> &nums) {
    float sum = 0;
    for (int i = 0; i < nums.size(); i++)
        sum += (float)nums[i];
    return sum / (float)(nums.size());
}

float standard_dev(vector<int> &nums) {
    float avg = average(nums);
    float sum = 0;
    for (int i = 0; i < nums.size(); i++)
        sum += pow((nums[i] - avg), 2);
    return sqrt(sum / (float)(nums.size()));
}

void Simulator::dump() {
    cout << "-{ General Statistics }-" << endl;
    cout << "Successful states: " << average(record_successful_states) << " +/- " << standard_dev(record_successful_states) << endl;
    cout << "Replans: " << average(record_failed_states) << " +/- " << standard_dev(record_failed_states) << endl;
    cout << "Actions: " << average(record_total_states) << " +/- " << standard_dev(record_total_states) << endl;
    cout << "State-Action Pairs: " << g_policy_size << endl;
    cout << "Strongly Cyclic: " << ((g_failed_open_states > 0) ? "False" : "True") << endl;
    cout << "Succeeded: " << record_succeeded << " / " << g_num_trials << endl;
    
    cout << "\n-{ Timing Statistics }-" << endl;
    cout << "Regression Computation: " << g_timer_regression << endl;
    cout << "Engine Initialization: " << g_timer_engine_init << endl;
    cout << "Search Time: " << g_timer_search << endl;
    cout << "Policy Construction: " << g_timer_policy_build << endl;
    cout << "Evaluating the policy: " << g_timer_policy_eval << endl;
    cout << "Just-in-case Repairs: " << g_timer_jit << endl;
    cout << "Total time: " << g_timer << endl;
}
