#include <cassert>
#include <iostream>
#include <limits>
using namespace std;

#include "globals.h"
#include "operator_cost.h"
#include "option_parser.h"
#include "search_engine.h"
#include "timer.h"
#include "policy-repair/deadend.h"

SearchEngine::SearchEngine(const Options &opts)
    : search_space(OperatorCost(opts.get_enum("cost_type"))),
      cost_type(OperatorCost(opts.get_enum("cost_type"))) {
    solved = false;
    if (opts.get<int>("bound") < 0) {
        cerr << "error: negative cost bound " << opts.get<int>("bound") << endl;
        exit_with(EXIT_INPUT_ERROR);
    }
    bound = opts.get<int>("bound");
}

SearchEngine::~SearchEngine() {
}

void SearchEngine::reset() {
    solved = false;
    search_space.reset();
    search_progress.reset();
    delete g_state_registry;
    g_state_registry = new StateRegistry;
    for (int i = 0; i < g_operators.size(); i++) {
        g_operators[i].unmark();
    }
}

void SearchEngine::statistics() const {
}

bool SearchEngine::found_solution() const {
    return solved;
}

const SearchEngine::Plan &SearchEngine::get_plan() const {
    assert(solved);
    return plan;
}

void SearchEngine::set_plan(const Plan &p) {
    solved = true;
    plan = p;
}

void SearchEngine::search() {
    
    if (g_record_online_deadends) {
        g_found_deadends.clear();
        delete g_temporary_deadends;
        g_temporary_deadends = new Policy();
    }
    
    initialize();
    Timer timer;
    while ((step() == IN_PROGRESS) && (g_timer_jit() < g_jic_limit))
        ;
    
    if (g_timer_jit() < g_jic_limit) {
        if (g_record_online_deadends && !g_limit_states && g_found_deadends.size() > 0) {
            g_replan_detected_deadends = true;
            //cout << "Number of online deadends: " << g_found_deadends.size() << endl;
            update_deadends(g_found_deadends);
        }
        if (search_progress.get_generated() > 2) {
            cout << "Generated " << search_progress.get_generated() << " state(s)." << endl;
            
            if (g_record_online_deadends && !g_limit_states)
                cout << "Dead ends: " << search_progress.get_deadend_states() << " state(s). ("
                     << g_found_deadends.size() << " recorded)" << endl;
            else
                cout << "Dead ends: " << search_progress.get_deadend_states() << " state(s)." << endl;
        }
        if (!g_silent_planning)
            cout << "Actual search time: " << timer
                << " [t=" << g_timer << "]" << endl;
    } else {
        g_replan_detected_deadends = true; // Just in case there is a risk to mark this as solved
        cout << "Killing search due to time limits." << endl;
    }
}

bool SearchEngine::check_goal_and_set_plan(const State &state) {
    if (test_goal(state)) {
        if (!g_silent_planning)
            cout << "Solution found!" << endl;
        Plan plan;
        search_space.trace_path(state, plan);
        set_plan(plan);
        return true;
    }
    return false;
}

void SearchEngine::save_plan_if_necessary() const {
    if (found_solution())
        save_plan(get_plan(), 0);
}

int SearchEngine::get_adjusted_cost(const Operator &op) const {
    return get_adjusted_action_cost(op, cost_type);
}

void SearchEngine::add_options_to_parser(OptionParser &parser) {
    ::add_cost_type_option_to_parser(parser);
    parser.add_option<int>(
        "bound",
        "exclusive depth bound on g-values. Cutoffs are always performed according to "
        "the real cost, regardless of the cost_type parameter", "infinity");
}
