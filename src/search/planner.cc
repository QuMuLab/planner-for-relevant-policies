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
    
    cout << "\n\nRegressing the plan..." << endl;
    list<RegressionStep *> regression_steps = perform_regression(engine->get_plan(), g_goal);
    for (list<RegressionStep *>::iterator op_iter = regression_steps.begin(); op_iter != regression_steps.end(); ++op_iter)
        (*op_iter)->dump();
    
    cout << "\n\nGenerating an initial policy..." << endl;
    Policy *pol = new Policy(regression_steps);
    
    //pol->update_policy(regression_steps);
    //pol->dump();
    
    cout << "\n\nComputing just-in-time repairs..." << endl;
    
    cout << "\n\nRunning the simulation..." << endl;
    Simulator *sim = new Simulator(pol, engine);
    sim->run();
    sim->dump();
    
    cout << "\n\n" << endl;

    return engine->found_solution() ? 0 : 1;
}
