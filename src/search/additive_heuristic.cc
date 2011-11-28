#include "additive_heuristic.h"

#include "operator.h"
#include "option_parser.h"
#include "plugin.h"
#include "state.h"

#include <cassert>
#include <vector>
using namespace std;




// construction and destruction
AdditiveHeuristic::AdditiveHeuristic(const Options &opts)
    : RelaxationHeuristic(opts),
      did_write_overflow_warning(false) {
    g_heuristic_for_reachability = this;
}

AdditiveHeuristic::~AdditiveHeuristic() {
}

void AdditiveHeuristic::write_overflow_warning() {
    if (!did_write_overflow_warning) {
        // TODO: Should have a planner-wide warning mechanism to handle
        // things like this.
        cout << "WARNING: overflow on h^add! Costs clamped to "
             << MAX_COST_VALUE << endl;
        cerr << "WARNING: overflow on h^add! Costs clamped to "
             << MAX_COST_VALUE << endl;
        did_write_overflow_warning = true;
    }
}

// initialization
void AdditiveHeuristic::initialize() {
    if (!g_silent_planning)
        cout << "Initializing additive heuristic..." << endl;
    RelaxationHeuristic::initialize();
}

// heuristic computation
void AdditiveHeuristic::setup_exploration_queue() {
    queue.clear();

    for (int var = 0; var < propositions.size(); var++) {
        for (int value = 0; value < propositions[var].size(); value++) {
            Proposition &prop = propositions[var][value];
            prop.cost = -1;
            prop.marked = false;
        }
    }

    // Deal with operators and axioms without preconditions.
    for (int i = 0; i < unary_operators.size(); i++) {
        UnaryOperator &op = unary_operators[i];
        
        op.unsatisfied_preconditions = op.precondition.size();
        op.cost = op.base_cost; // will be increased by precondition costs
        
        if (op.unsatisfied_preconditions == 0)
            enqueue_if_necessary(op.effect, op.base_cost, &op);
    }
}

void AdditiveHeuristic::setup_exploration_queue_state(const State &state) {
    for (int var = 0; var < propositions.size(); var++) {
        if (state_var_t(-1) == state[var]) {
            for (int val = 0; val < propositions[var].size(); val++) {
                Proposition *init_prop = &propositions[var][val];
                enqueue_if_necessary(init_prop, 0, 0);
            }
        } else {
            Proposition *init_prop = &propositions[var][state[var]];
            enqueue_if_necessary(init_prop, 0, 0);
        }
    }
}

void AdditiveHeuristic::relaxed_exploration() {
    int unsolved_goals = goal_propositions.size();
    while (!queue.empty()) {
        pair<int, Proposition *> top_pair = queue.pop();
        int distance = top_pair.first;
        Proposition *prop = top_pair.second;
        int prop_cost = prop->cost;
        assert(prop_cost >= 0);
        assert(prop_cost <= distance);
        if (prop_cost < distance)
            continue;
        if (prop->is_goal && --unsolved_goals == 0)
            return;
        const vector<UnaryOperator *> &triggered_operators =
            prop->precondition_of;
        for (int i = 0; i < triggered_operators.size(); i++) {
            
            UnaryOperator *unary_op = triggered_operators[i];
            increase_cost(unary_op->cost, prop_cost);
            unary_op->unsatisfied_preconditions--;
            // HAZ: This assertion no longer holds with forbidden operators
            //assert(unary_op->unsatisfied_preconditions >= 0);
            
            // HAZ: This check exists to ensure that we aren't using forbidden
            //       operators as achievers in the first layer. Future layers
            //       is fine, so prop_cost > 0 will let it pass.
            if ((unary_op->unsatisfied_preconditions <= 0) &&
                (!g_detect_deadends || (unary_op->cost != unary_op->base_cost) || 
                (0 == forbidden_ops.count(g_operators[triggered_operators[i]->operator_no].get_nondet_name()))))
                    enqueue_if_necessary(unary_op->effect,
                                         unary_op->cost,
                                         unary_op);
            
            // HAZ: If we have a unary operator with an effect that triggers
            //       a forbidden operator that is already satisfied (precondition
            //       wise), then we should trigger the forbidden op. This arises
            //       in rare cases where the forbidden op is required later in
            //       the plan, and this approach relies on the fact that all of
            //       the initial state props are handled first.
            if (g_detect_deadends && (forbidden_ops.size() > 0)) {
                //unary_op->effect->cost != -1 &&
                //unary_op->effect->cost <= unary_op->cost) {
                
                const vector<UnaryOperator *> &new_triggered_operators = unary_op->effect->precondition_of;
        
                for (int j = 0; j < new_triggered_operators.size(); j++) {
                    if (0 != forbidden_ops.count(g_operators[new_triggered_operators[j]->operator_no].get_nondet_name())) {
                        
                        if (new_triggered_operators[j]->unsatisfied_preconditions <= 0) {
                            increase_cost(new_triggered_operators[j]->cost, unary_op->cost);
                            enqueue_if_necessary(new_triggered_operators[j]->effect,
                                                 new_triggered_operators[j]->cost,
                                                 new_triggered_operators[j]);
                        }
                    }
                }
            }
        }
    }
}

void AdditiveHeuristic::mark_preferred_operators(
    const State &state, Proposition *goal) {
    if (!goal->marked) { // Only consider each subgoal once.
        goal->marked = true;
        UnaryOperator *unary_op = goal->reached_by;
        if (unary_op) { // We have not yet chained back to a start node.
            for (int i = 0; i < unary_op->precondition.size(); i++)
                mark_preferred_operators(state, unary_op->precondition[i]);
            int operator_no = unary_op->operator_no;
            if (unary_op->cost == unary_op->base_cost && operator_no != -1) {
                // Necessary condition for this being a preferred
                // operator, which we use as a quick test before the
                // more expensive applicability test.
                // If we had no 0-cost operators and axioms to worry
                // about, this would also be a sufficient condition.
                const Operator *op = &g_operators[operator_no];
                if (op->is_applicable(state))
                    set_preferred(op);
            }
        }
    }
}

int AdditiveHeuristic::compute_add_and_ff(const State &state) {
    setup_exploration_queue();
    setup_exploration_queue_state(state);
    relaxed_exploration();

    int total_cost = 0;
    for (int i = 0; i < goal_propositions.size(); i++) {
        int prop_cost = goal_propositions[i]->cost;
        if (prop_cost == -1)
            return DEAD_END;
        increase_cost(total_cost, prop_cost);
    }
    return total_cost;
}

int AdditiveHeuristic::compute_heuristic(const State &state) {
    int h = compute_add_and_ff(state);
    if (h != DEAD_END) {
        for (int i = 0; i < goal_propositions.size(); i++)
            mark_preferred_operators(state, goal_propositions[i]);
    }
    return h;
}

static ScalarEvaluator *_parse(OptionParser &parser) {
    Heuristic::add_options_to_parser(parser);
    Options opts = parser.parse();
    if (parser.dry_run())
        return 0;
    else
        return new AdditiveHeuristic(opts);
}

static Plugin<ScalarEvaluator> _plugin("add", _parse);
