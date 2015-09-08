#include "globals.h"
#include "operator.h"
#include "option_parser.h"
#include "ext/tree_util.hh"
#include "timer.h"
#include "utilities.h"
#include "search_engine.h"
#include "policy-repair/regression.h"
#include "policy-repair/simulator.h"
#include "policy-repair/policy.h"
#include "policy-repair/jit.h"
#include "policy-repair/partial_state.h"


#include <iostream>
#include <list>
#include <new>
using namespace std;


int main(int argc, const char **argv) {
    register_event_handlers();

    if (argc < 2) {
        cout << OptionParser::usage(argv[0]) << endl;
        exit_with(EXIT_INPUT_ERROR);
    }

    if (string(argv[1]).compare("--help") != 0)
        read_everything(cin);

    SearchEngine *engine = 0;
    g_policy = 0;
    
    g_timer_regression.stop();
    g_timer_simulator.stop();
    g_timer_engine_init.stop();
    g_timer_search.stop();
    g_timer_policy_build.stop();
    g_timer_policy_eval.stop();
    g_timer_policy_use.stop();
    g_timer_jit.stop();
    
    g_timer_regression.reset();
    g_timer_simulator.reset();
    g_timer_engine_init.reset();
    g_timer_search.reset();
    g_timer_policy_build.reset();
    g_timer_policy_eval.reset();
    g_timer_policy_use.reset();
    g_timer_jit.reset();

    //the input will be parsed twice:
    //once in dry-run mode, to check for simple input errors,
    //then in normal mode
    g_timer_engine_init.resume();
    try {
        OptionParser::parse_cmd_line(argc, argv, true);
        engine = OptionParser::parse_cmd_line(argc, argv, false);
    } catch (ParseError &pe) {
        cerr << pe << endl;
        exit_with(EXIT_INPUT_ERROR);
    }
    g_timer_engine_init.stop();
    
    /* HAZ: Unfortunately, this must go here (as supposed to globals.cc)
     *      since we need to know if g_detect_deadends is true or not. */
    if (g_detect_deadends) {
        generate_regressable_ops();
    }
    /* HAZ: We create the policies even if we aren't using deadends, as
     *      they may be consulted by certain parts of the code. */
    g_deadend_policy = new Policy();
    g_deadend_states = new Policy();
    g_temporary_deadends = new Policy();
    
    
    /***************************************
     * Assert the settings are consistent. *
     ***************************************/
    if (((g_record_online_deadends || g_generalize_deadends) && !g_detect_deadends) ||
        ((g_partial_planlocal || g_plan_locally_limited) && !g_plan_locally) ||
        (g_optimized_scd && (g_jic_limit == 0)) ||
        (g_forgetpolicy && (g_jic_limit > 0))) {
            
        cout << "\n  Parameter Error: Make sure that the set of parameters is consistent.\n" << endl;
        exit(0);
    }
    
    
    
    /*********************
     * Handle JIC Limits *
     *********************/
     
    cout << "\nTotal allotted time (s): " << g_jic_limit << endl;
    
    // If we are going to do a final FSAP-free round, then we modify the
    //  time limits to give a 50/50 split between the JIC phase and final
    //  round phase
    double jic_ratio = 0.5;
    if (g_final_fsap_free_round)
        g_jic_limit *= jic_ratio;
    
    cout << "Max time for core JIC (remaining used in final-round repairs): " << g_jic_limit << endl;
    
    // Adjust the g_jic_limit so the epochs are handled properly
    int epochs_remaining = g_num_epochs;
    double single_jic_limit = g_jic_limit / (double)g_num_epochs;
    g_jic_limit = single_jic_limit;
    
    cout << "Max time for each of the " << epochs_remaining << " epochs: " << g_jic_limit << endl << endl;
    
    
    
    // We start the jit timer here since we should include the initial search / policy construction
    g_timer_jit.resume();
    g_timer_search.resume();
    engine->search();
    g_timer_search.stop();
    
    engine->save_plan_if_necessary();
    engine->statistics();
    engine->heuristic_statistics();
    
    cout << "Initial search time: " << g_timer_search << endl;
    cout << "Initial total time: " << g_timer << endl;
    
    if (!engine->found_solution()) {
        cout << "No solution -- aborting repairs." << endl;
        exit(1);
    }
    
    cout << "\n\nCreating the simulator..." << endl;
    Simulator *sim = new Simulator(engine, argc, argv, !g_silent_planning);
    
    cout << "\n\nRegressing the plan..." << endl;
    list<PolicyItem *> regression_steps = perform_regression(engine->get_plan(), g_matched_policy, 0, true);
    
    cout << "\n\nGenerating an initial policy..." << endl;
    g_policy = new Policy();
    g_policy->update_policy(regression_steps);
    g_best_policy = g_policy;
    g_best_policy_score = g_policy->get_score();
    
    if (g_sample_for_depth1_deadends)
        sample_for_depth1_deadends(engine->get_plan(), new PartialState(g_initial_state()));
    
    cout << "\n\nComputing just-in-time repairs..." << endl;
    bool changes_made = true;
    while (changes_made) {
        changes_made = perform_jit_repairs(sim);
        if (!g_silent_planning)
            cout << "Finished repair round." << endl;
        
        if (g_timer_jit() >= g_jic_limit) {
            epochs_remaining--;
            if (epochs_remaining > 0)
                g_jic_limit += single_jic_limit;
        }
        
        // Check if we should re-run the repairs with forbidden ops used
        //  in the heurstic computation.
        if (!changes_made && !g_check_with_forbidden &&
            g_detect_deadends && !(g_policy->is_strong_cyclic()) &&
            (g_timer_jit() < g_jic_limit)) {
            
            g_check_with_forbidden = true;
            changes_made = true;
            if (g_best_policy != g_policy)
                delete g_policy;
            g_policy = new Policy();
            
            // We need to reset the deadends since they may have been
            //  generated based on faulty heuristic computations that
            //  ignored the forbidden state-action pairs.
            if (g_deadend_policy)
                delete g_deadend_policy;
            if (g_deadend_states)
                delete g_deadend_states;
            g_deadend_policy = new Policy();
            g_deadend_states = new Policy();
            
        }
    }
    if (!g_silent_planning)
        cout << "Done repairing..." << endl;
    g_timer_jit.stop();

    // Use the best policy found so far
    if (g_policy && g_best_policy && (g_best_policy != g_policy)) {
        if (g_best_policy->get_score() > g_policy->get_score())
            g_policy = g_best_policy;
    }
    
    if (g_final_fsap_free_round)
        g_jic_limit /= jic_ratio;

    if (!(g_policy->is_strong_cyclic()) && g_final_fsap_free_round) {
    
        bool os1 = g_detect_deadends;
        bool os2 = g_generalize_deadends;
        bool os3 = g_record_online_deadends;
        bool os4 = g_force_limit_states;
        int  os5 = g_limit_states_max;
        
        g_detect_deadends = false;
        g_generalize_deadends = false;
        g_record_online_deadends = false;
        g_force_limit_states = true;
        g_limit_states_max = 1000;
        
        g_policy->return_if_possible = true;
        g_policy->mark_incomplete();
        
        cout << "\n\nDoing one final JIC round ignoring FSAPs for unhandled states." << endl;
        g_timer_jit.resume();
        perform_jit_repairs(sim);
        g_timer_jit.stop();
        
        g_policy->return_if_possible = false;
        
        g_detect_deadends = os1;
        g_generalize_deadends = os2;
        g_record_online_deadends = os3;
        g_force_limit_states = os4;
        g_limit_states_max = os5;
    }
    
    if (g_optimized_scd) {
        cout << "\n\nRunning a final SCD check..." << endl;
        vector< DeadendTuple * > failed_states; // The failed states (used for creating deadends)
        g_policy->init_scd(true);
        bool made_change = true; // This becomes false again eventually
        while (made_change)
            made_change = g_policy->step_scd(failed_states, false);
    }
    
    // Allow selection of a forbidden action when no legal actions exist
    g_policy->return_if_possible = true;

    if (g_optimize_final_policy) {
        g_timer_policy_build.resume();
        
        cout << "\n\nRunning a final JIT repair to see which pairs are relevant..." << endl;
        g_record_relevant_pairs = true;
        perform_jit_repairs(sim);
        g_record_relevant_pairs = false;
        cout << "...and creating the new policies..." << endl;
        
        g_timer_policy_build.stop();
        
        // Rebuild the policies
        Policy * newPol = new Policy();
        Policy * newFSAP = new Policy();
        
        list<PolicyItem *> reg_items;
        list<PolicyItem *> fsap_items;
        
        g_policy->copy_relevant_items(reg_items, true);
        g_deadend_policy->copy_relevant_items(fsap_items);
        
        newPol->update_policy(reg_items);
        newFSAP->update_policy(fsap_items);
        
        // Re-enable the return_if_possible and other settings
        newPol->return_if_possible = true;
        if (g_policy->is_complete())
            newPol->mark_complete();
        if (g_policy->is_strong_cyclic())
            newPol->mark_strong();
        
        // DO NOT DELETE: It deletes every PolicyItem
        //delete g_policy;
        //delete g_deadend_policy;
        
        g_policy = newPol;
        g_deadend_policy = newFSAP;
        
    }
    
    // Reset the deadend and scd settings for the online simulation(s)
    g_detect_deadends = false;
    g_generalize_deadends = false;
    g_record_online_deadends = false;
    g_optimized_scd = false;

    cout << "\n\nRunning the simulation..." << endl;
    g_timer_simulator.resume();
    sim->run();
    g_timer_simulator.stop();
    
    
    g_timer.stop();
    
    
    cout << "\n\n" << endl;
    sim->dump();
    cout << "\n\n" << endl;
    
    if (1 == g_dump_policy) {
        
        cout << "Dumping the policy and fsaps..." << endl;
        ofstream outfile;
        
        outfile.open("policy.out", ios::out);
        g_policy->generate_cpp_input(outfile);
        outfile.close();
        
        outfile.open("policy.fsap", ios::out);
        g_deadend_policy->generate_cpp_input(outfile);
        outfile.close();
        
    } else if (2 == g_dump_policy) {
        cout << "Dumping the policy and fsaps..." << endl;
        g_policy->dump_human_policy();
        g_deadend_policy->dump_human_policy(true);
    }
    
    if (g_policy->is_strong_cyclic())
        exit_with(EXIT_STRONG_CYCLIC);
    else
        exit_with(EXIT_NOT_STRONG_CYCLIC);
    
}
