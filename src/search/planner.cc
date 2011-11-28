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


#include <iostream>
#include <list>
using namespace std;



int main(int argc, const char **argv) {
    register_event_handlers();

    if (argc < 2) {
        cout << OptionParser::usage(argv[0]) << endl;
        exit(1);
    }

    if (string(argv[1]).compare("--help") != 0)
        read_everything(cin);

    SearchEngine *engine = 0;
    g_policy = 0;
    
    g_timer_regression.stop();
    g_timer_engine_init.stop();
    g_timer_search.stop();
    g_timer_policy_build.stop();
    g_timer_policy_eval.stop();
    g_timer_policy_use.stop();
    g_timer_jit.stop();
    
    g_timer_regression.reset();
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
        cout << pe << endl;
        exit(1);
    }
    g_timer_engine_init.stop();
    
    /* HAZ: Unfortunately, this must go here (as supposed to globals.cc)
     *      since we need to know if g_detect_deadends is true or not. */
    if (g_detect_deadends) {
        generate_regressable_ops();
        g_deadend_policy = new Policy();
        g_deadend_states = new Policy();
    }
    
    
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
    
    g_silent_planning = true;
    
    cout << "\n\nCreating the simulator..." << endl;
    Simulator *sim = new Simulator(engine, argc, argv, !g_silent_planning);
    
    cout << "\n\nRegressing the plan..." << endl;
    list<PolicyItem *> regression_steps = perform_regression(engine->get_plan(), g_goal, 0, true);
    
    cout << "\n\nGenerating an initial policy..." << endl;
    g_policy = new Policy(regression_steps);
    g_best_policy = g_policy;
    g_best_policy_score = g_policy->get_score();
    
    cout << "\n\nComputing just-in-time repairs..." << endl;
    //g_timer_jit.resume(); // Placed above to include the initial search time
    bool changes_made = true;
    while (changes_made) {
        changes_made = perform_jit_repairs(sim);
        if (!g_silent_planning)
            cout << "Finished repair round." << endl;
        
        // Check if we should re-run the repairs with forbidden ops used
        //  in the heurstic computation.
        if (!changes_made && !g_check_with_forbidden &&
            g_detect_deadends && !(g_policy->is_strong_cyclic())) {
            
            g_check_with_forbidden = true;
            changes_made = true;
            if (g_best_policy != g_policy)
                delete g_policy;
            g_policy = new Policy();
            
            // We need to reset the deadends since they may have been
            //  generated based on faulty heuristic computations that
            //  ignored the forbidden state-action pairs.
            g_deadend_policy = new Policy();
            g_deadend_states = new Policy();
            
        }
    }
    if (!g_silent_planning)
        cout << "Done repairing..." << endl;
    g_timer_jit.stop();

    cout << "\n\nRunning the simulation..." << endl;
    sim->run();
    
    cout << "\n\n" << endl;
    
    g_timer.stop();
    sim->dump();
    
    cout << "\n\n" << endl;

    return sim->succeeded ? 0 : 1;
}
