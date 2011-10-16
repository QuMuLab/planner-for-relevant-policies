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

    //the input will be parsed twice:
    //once in dry-run mode, to check for simple input errors,
    //then in normal mode
    try {
        OptionParser::parse_cmd_line(argc, argv, true);
        engine = OptionParser::parse_cmd_line(argc, argv, false);
    } catch (ParseError &pe) {
        cout << pe << endl;
        exit(1);
    }

    Timer search_timer;
    engine->search();
    search_timer.stop();
    g_timer.stop();

    engine->save_plan_if_necessary();
    engine->statistics();
    engine->heuristic_statistics();
    cout << "Search time: " << search_timer << endl;
    cout << "Total time: " << g_timer << endl;
    
    if (!engine->found_solution()) {
        cout << "No solution -- aborting repairs." << endl;
        exit(1);
    }
    cout << "\n\nRegressing the plan..." << endl;
    list<RegressionStep *> regression_steps = perform_regression(engine->get_plan(), g_goal, 0, true);
    for (list<RegressionStep *>::iterator op_iter = regression_steps.begin(); op_iter != regression_steps.end(); ++op_iter)
        (*op_iter)->dump();
    
    cout << "\n\nGenerating an initial policy..." << endl;
    g_policy = new Policy(regression_steps);
    
    cout << "\n\nComputing just-in-time repairs..." << endl;
    bool changes_made = true;
    while (changes_made) {
        changes_made = perform_jit_repairs(engine, argc, argv, 0.0);
        cout << "Finished repair round." << endl;
    }
    cout << "Done repairing..." << endl;
    engine = OptionParser::parse_cmd_line(argc, argv, false);
    
    cout << "\n\nRunning the simulation..." << endl;
    Simulator *sim = new Simulator(engine, argc, argv, false);
    sim->run();
    
    cout << "\n\n" << endl;
    
    sim->dump();
    
    cout << "\n\n" << endl;

    return sim->found_solution ? 0 : 1;
}
