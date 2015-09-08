#include "simulator.h"
#include "../option_parser.h"

Simulator::Simulator(SearchEngine *eng, int _argc, const char **_argv, bool verb) :
                    engine(eng), argc(_argc), argv(_argv), verbose(verb), found_solution(false), succeeded(false) {
    current_state = new PartialState(g_initial_state());
    successful_states = 0;
    failed_states = 0;
    record_succeeded = 0;
    record_depth_limit = 0;
}

Simulator::Simulator(bool verb) : verbose(verb), found_solution(false), succeeded(false) {
    current_state = new PartialState(g_initial_state());
    successful_states = 0;
    failed_states = 0;
    record_succeeded = 0;
    record_depth_limit = 0;
}

void Simulator::run() {
    for (int i = 0; i < g_num_trials; i++) {
        
        if (g_forgetpolicy) {
            delete g_policy;
            g_policy = new Policy();

            if (g_deadend_policy)
                delete g_deadend_policy;
            if (g_deadend_states)
                delete g_deadend_states;
            g_deadend_policy = new Policy();
            g_deadend_states = new Policy();
        }
        
        run_once(!g_replan_during_simulation);
        
        record_stats();
        
    }
}

void Simulator::record_stats() {
    record_successful_states.push_back(successful_states);
    record_failed_states.push_back(failed_states);
    record_total_states.push_back(successful_states + failed_states);
    if (succeeded)
        record_succeeded++;
    if (failed_states + successful_states >= g_trial_depth)
        record_depth_limit++;
}

void Simulator::run_once(bool stop_on_failure, Policy *pol) {
    found_solution = false;
    succeeded = false;
    RegressionStep * current_step;
    successful_states = 0;
    failed_states = 0;
    
    PartialState *orig_init_state = new PartialState(g_initial_state());
    current_state = new PartialState(g_initial_state());
    
    reset_goal();
    
    // To prevent infinite loops with 0-probability exit, we limit the loops
    while(!found_solution && (failed_states + successful_states < g_trial_depth)) {
        // Get the best action (if any)
        current_step = pol->get_best_step(*current_state);
        
        if (current_step) {
            
            successful_states++;
            
            if (current_step->is_goal) {
                if (verbose || ((1 == g_num_trials) && !stop_on_failure))
                    cout << "...achieved the goal!" << endl;
                succeeded = true;
                found_solution = true;
            } else {
                // Execute the non-deterministic action
                execute_action(current_step->op);
            }
        
        } else {
            failed_states++;
            if (stop_on_failure || !replan()) {
                if (verbose || ((1 == g_num_trials) && !stop_on_failure))
                    cout << "Got into a dead-end state..." << endl;
                succeeded = false;
                found_solution = true;
            }
        }
    }
    
    g_state_registry->reset_initial_state();
    for (int i = 0; i < g_variable_name.size(); i++)
        g_initial_state_data[i] = (*orig_init_state)[i];
}

bool Simulator::execute_action(const Operator *op) {
    
    if (verbose) {
        cout << "\nExpected operator:" << endl << "  ";
        op->dump();
    }
    
    // Choose the op
    int choice = g_rng.next(g_nondet_mapping[op->nondet_index]->size());
    Operator *chosen = (*(g_nondet_mapping[op->nondet_index]))[choice];
    
    if (verbose) {
        cout << "Chosen operator:" << endl << "  ";
        chosen->dump();
    }
    
    PartialState *old_state = current_state;
    current_state = new PartialState(*old_state, *chosen);
    delete old_state;
    
    return (op->get_name() == chosen->get_name());
}

void Simulator::reset_goal() {
    g_goal.clear();
    for (int i = 0; i < g_goal_orig.size(); i++)
        g_goal.push_back(make_pair(g_goal_orig[i].first, g_goal_orig[i].second));
}

bool Simulator::replan() {
    
    g_replan_detected_deadends = false;
    
    // If the policy is complete, searching further won't help us
    if (g_policy->is_complete())
        return false;
    
    // If we are detecting deadends, and know this is one, don't even try
    if (g_detect_deadends) {
        if (g_deadend_states->check_match(*current_state, false))
            return false;
    }

    // If we can detect that this is a deadend for the original goal, forget about it
    if (is_deadend(*current_state))
        return false;
    
    if (verbose)
        cout << "\nRequired to replan..." << endl;
    
    if (!current_state) {
        cout << "Error: No current state for the replan." << endl;
        exit(0);
    }
    
    if (verbose)
        cout << "Creating initial state." << endl;
    
    g_state_registry->reset_initial_state();
    for (int i = 0; i < g_variable_name.size(); i++)
        g_initial_state_data[i] = (*current_state)[i];
    
    if (g_plan_locally) {
        if (verbose)
            cout << "Resetting the goal state." << endl;
        
        g_goal.clear();
        for (int i = 0; i < g_variable_name.size(); i++) {
            if ((*current_goal)[i] != -1)
                g_goal.push_back(make_pair(i, (*current_goal)[i]));
        }
    }
    
    if (verbose)
        cout << "Creating new engine." << endl;
    bool engine_ready = true;
    g_timer_engine_init.resume();
    try {
        //engine = OptionParser::parse_cmd_line(argc, argv, false);
        engine->reset();
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
            //engine = OptionParser::parse_cmd_line(argc, argv, false);
            engine->reset();
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
        
        if (try_again)
            g_limit_states = true;
        g_timer_search.resume();
        engine->search();
        g_timer_search.stop();
        g_limit_states = false;
        
        if (engine->found_solution()) {
            
            if (verbose) {
                engine->save_plan_if_necessary();
                engine->statistics();
                engine->heuristic_statistics();
            }
            
            if (verbose)
                cout << "Building the regression list." << endl;
            list<PolicyItem *> regression_steps = perform_regression(engine->get_plan(), g_matched_policy, g_matched_distance, g_policy->empty());
            
            if (verbose)
                cout << "Updating the policy." << endl;
            g_policy->update_policy(regression_steps);
            
            reset_goal();
            
            if (g_sample_for_depth1_deadends) {
                if (verbose)
                    cout << "Analyzing for extra deadends (v1)." << endl;
                sample_for_depth1_deadends(engine->get_plan(), new PartialState(g_initial_state()));
            }
            
            return true;
            
        } else {
            
            reset_goal();
            
            if (try_again) {
                //delete engine;
                
                if (verbose)
                    cout << "Creating new engine." << endl;
                g_timer_engine_init.resume();
                try {
                    //engine = OptionParser::parse_cmd_line(argc, argv, false);
                    engine->reset();
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
                    
                    if (verbose) {
                        engine->save_plan_if_necessary();
                        engine->statistics();
                        engine->heuristic_statistics();
                    }
                    
                    if (verbose)
                        cout << "Building the regression list." << endl;
                    list<PolicyItem *> regression_steps = perform_regression(engine->get_plan(), g_matched_policy, g_matched_distance, g_policy->empty());
                    
                    if (verbose)
                        cout << "Updating the policy." << endl;
                    g_policy->update_policy(regression_steps);
                    
                    if (g_sample_for_depth1_deadends) {
                        if (verbose)
                            cout << "Analyzing for extra deadends (v2)." << endl;
                        sample_for_depth1_deadends(engine->get_plan(), new PartialState(g_initial_state()));
                    }
                    
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
    cout << "                  -{ General Statistics }-\n" << endl;
    
    if (g_repeat_fsap_backwards)
        cout << "             Repeat FSAP Count: " << g_repeat_fsap_count << endl;
    
    cout << "        FSAP Combination Count: " << g_combined_count << endl;
    cout << "       Monotonicity violations: " << g_monotonicity_violations << endl;
    cout << "             Successful states: " << average(record_successful_states) << " +/- " << standard_dev(record_successful_states) << endl;
    cout << "                       Replans: " << average(record_failed_states) << " +/- " << standard_dev(record_failed_states) << endl;
    cout << "                       Actions: " << average(record_total_states) << " +/- " << standard_dev(record_total_states) << endl;
    cout << "             Recorded Deadends: " << g_deadend_states->get_size() << endl;
    cout << "            State-Action Pairs: " << g_policy->get_size() << endl;
    cout << "  Forbidden State-Action Pairs: " << g_deadend_policy->get_size() << endl;
    cout << "               Strongly Cyclic: " << (g_policy->is_strong_cyclic() ? "True" : "False") << endl;
    cout << "                  Policy Score: " << g_policy->get_score() << endl;
    cout << "                     Succeeded: " << record_succeeded << " / " << g_num_trials << endl;
    cout << " Depth limit (of " << g_trial_depth << ") reached: " << record_depth_limit << " / " << g_num_trials << endl;
    
    cout << "\n\n                  -{ Timing Statistics }-\n" << endl;
    cout << "        Regression Computation: " << g_timer_regression << endl;
    cout << "         Engine Initialization: " << g_timer_engine_init << endl;
    cout << "                   Search Time: " << g_timer_search << endl;
    cout << "           Policy Construction: " << g_timer_policy_build << endl;
    cout << " Evaluating the policy quality: " << g_timer_policy_eval << endl;
    cout << "              Using the policy: " << g_timer_policy_use << endl;
    cout << "          Just-in-case Repairs: " << g_timer_jit << endl;
    cout << "                Simulator time: " << g_timer_simulator << endl;
    cout << "                    Total time: " << g_timer << endl;
}
