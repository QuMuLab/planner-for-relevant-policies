#include "regression.h"
#include "policy.h"

void RegressionStep::dump() const {
    cout << "Regression Step (" << this << ")" << endl;
    cout << " Distance: " << distance << endl;
    cout << " Relevant: " << relevant << endl;
    cout << " SC: " << is_sc << endl;
    if (!is_goal) {
        cout << " -{ Operator }-" << endl;
        op->dump();
    } else {
        cout << " -{ Goal }-" << endl;
    }
    cout << "\n -{ State }-" << endl;
    state->dump_pddl();
    cout << "" << endl;
}

string RegressionStep::get_name() {
    if (is_goal)
        return "goal / SC / d=0";
    else
        return op->get_nondet_name() + " / " + (is_sc ? "SC" : "NSC") + " / d=" + static_cast<ostringstream*>( &(ostringstream() << distance) )->str();
}

void NondetDeadend::dump() const {
    cout << "Non-deterministic deadend:" << endl;
    cout << "Operator: " << g_operators[op_index].get_name() << endl;
    cout << " -{ State }-" << endl;
    state->dump_pddl();
    cout << "" << endl;
}

string NondetDeadend::get_name() {
    return (*(g_nondet_mapping[op_index]))[0]->get_nondet_name();
}

int NondetDeadend::get_index() {
    return op_index;
}

int PolicyItem::generality() {
    if (-1 != _generality) {
        _generality = 0;
        for (int i = 0; i < g_variable_name.size(); i++) {
            if (-1 == (*state)[i]) {
                _generality++;
            }
        }
    }

    return _generality;
}

void RegressableOperator::dump() const {
    cout << "Regressable operator:" << endl;
    cout << " -{ Operator }-" << endl;
    op->dump();
    cout << " -{ State }-" << endl;
    state->dump_pddl();
    cout << "" << endl;
}

string RegressableOperator::get_name() {
    return op->get_name();
}

bool RegressableOperator::check_relevance(const PartialState &ps) {

    bool debug = false;

    for (int i = 0; i < op->get_pre_post().size(); i++) {
        if (-1 != ps[op->get_pre_post()[i].var])
            return true;
    }

    for (int i = 0; i < op->get_prevail().size(); i++) {
        if (-1 != ps[op->get_prevail()[i].var])
            return true;
    }

    if (debug) {
        cout << "\nReturning false for check_relevance using operator..." << endl;
        op->dump();
        cout << "...and partial state..." << endl;
        ps.dump_pddl();
    }

    return false;
}



list<PolicyItem *> perform_regression(const SearchEngine::Plan &plan, RegressionStep *goal_step, int distance, bool create_goal) {
    g_timer_regression.resume();
    list<PolicyItem *> reg_steps;
    PartialState *s = new PartialState(g_initial_state());

    vector<PartialState *> states;
    states.push_back(s);

    for (int i = 0; i < plan.size(); i++) {
        s = new PartialState(*s, *plan[i]);
        states.push_back(s);
    }

    if (g_fullstate) {

        if (create_goal) {

            PartialState *g = new PartialState(*(goal_step->state));

            reg_steps.push_back(new RegressionStep(g, distance));

        } else {
            reg_steps.push_back(new RegressionStep(states.back(), distance));
        }

        // Remove the full goal state (we still keep the partial goal state if need be)
        states.pop_back();

        for (int i = plan.size() - 1; i >= 0; i--) {
            RegressionStep *next = (RegressionStep*)reg_steps.back();
            reg_steps.push_back(new RegressionStep(*plan[i], states.back(), ++distance, next));
            next->prev = (RegressionStep*)reg_steps.back();
            states.pop_back();
        }

        assert(states.empty());

    } else {
        s = new PartialState(*(goal_step->state));

        reg_steps.push_back(new RegressionStep(s, distance));

        for (int i = plan.size() - 1; i >= 0; i--) {

            RegressionStep *next = (RegressionStep*)reg_steps.back();

            PartialState *regressed = new PartialState(*(next->state), *plan[i], false, states[i]);

            reg_steps.push_back(new RegressionStep(*plan[i], regressed, ++distance, next));

            next->prev = (RegressionStep*)reg_steps.back();

            // Strengthen the step so it doesn't fire an FSAP at some
            // some point. Strengthening is sufficient but not neccessary
            ((RegressionStep*)reg_steps.back())->strengthen(states[i]);

        }
    }

    if (!create_goal) {
        delete reg_steps.front();
        reg_steps.pop_front();
        ((RegressionStep*)reg_steps.front())->next = goal_step;
    }

    for (int i = 0; i < states.size(); i++)
        delete states[i];
    states.clear();

    g_timer_regression.stop();
    return reg_steps;
}

void generate_regressable_ops() {

    list<PolicyItem *> reg_steps;
    list<PolicyItem *> cond_reg_steps;

    PartialState *s;
    for (int i = 0; i < g_operators.size(); i++) {

        // First, consider operators that lack conditional effects
        if (0 == g_nondet_conditional_mask[g_operators[i].nondet_index]->size()) {
            s = new PartialState();

            // Only applicable if the prevail and post conditions currently hold.
            for (int j = 0; j < g_operators[i].get_pre_post().size(); j++) {
                (*s)[g_operators[i].get_pre_post()[j].var] = int(g_operators[i].get_pre_post()[j].post);
            }

            for (int j = 0; j < g_operators[i].get_prevail().size(); j++) {
                (*s)[g_operators[i].get_prevail()[j].var] = int(g_operators[i].get_prevail()[j].prev);
            }

            reg_steps.push_back(new RegressableOperator(g_operators[i], s));
        }

        // Next, consider operators that have conditional effects that are consistent
        else {
            s = new PartialState();
            bool consistent = true;
            int var,val;

            // Ensure that the conditional effect preconditions are all consistent to fire.
            for (int j = 0; consistent && (j < g_operators[i].get_pre_post().size()); j++) {

                var = g_operators[i].get_pre_post()[j].var;
                val = g_operators[i].get_pre_post()[j].pre;

                if ((-1 != (*s)[var]) && (val != (*s)[var])) {
                    consistent = false;
                    break;
                } else {
                    (*s)[var] = val;
                }

                for (int k = 0; k < g_operators[i].get_pre_post()[j].cond.size(); k++) {

                    var = g_operators[i].get_pre_post()[j].cond[k].var;
                    val = g_operators[i].get_pre_post()[j].cond[k].prev;

                    if ((-1 != (*s)[var]) && (val != (*s)[var])) {
                        consistent = false;
                        break;
                    } else {
                        (*s)[var] = val;
                    }
                }

            }

            for (int j = 0; consistent && (j < g_operators[i].get_prevail().size()); j++) {

                var = g_operators[i].get_prevail()[j].var;
                val = g_operators[i].get_prevail()[j].prev;

                if ((-1 != (*s)[var]) && (val != (*s)[var])) {
                    consistent = false;
                    break;
                } else {
                    (*s)[var] = val;
                }

            }


            // Reset the state for checking the post conditions
            delete s;
            s = new PartialState();


            // Only makes sense to continue if it is consistent so far
            if (consistent) {
                // Only applicable if the prevail and post conditions currently hold.
                for (int j = 0; j < g_operators[i].get_pre_post().size(); j++) {

                    var = g_operators[i].get_pre_post()[j].var;
                    val = g_operators[i].get_pre_post()[j].post;

                    if ((-1 != (*s)[var]) && (val != (*s)[var])) {
                        consistent = false;
                        break;
                    } else {
                        (*s)[var] = val;
                    }

                }

                for (int j = 0; j < g_operators[i].get_prevail().size(); j++) {

                    var = g_operators[i].get_prevail()[j].var;
                    val = g_operators[i].get_prevail()[j].prev;

                    if ((-1 != (*s)[var]) && (val != (*s)[var])) {
                        consistent = false;
                        break;
                    } else {
                        (*s)[var] = val;
                    }

                }
            }

            if (consistent)
                cond_reg_steps.push_back(new RegressableOperator(g_operators[i], s));
            else
                delete s;
        }
    }

    g_regressable_ops = new Policy();
    g_regressable_ops->update_policy(reg_steps);
    g_regressable_cond_ops = new Policy();
    g_regressable_cond_ops->update_policy(cond_reg_steps);

}

void RegressionStep::strengthen(PartialState *s) {

    if (is_goal)
        return;

    vector<PolicyItem *> reg_items;
    g_deadend_policy->generate_applicable_items(*state, reg_items, true, false);

    // Each item could potentially be a forbidden state-action pair
    for (int i = 0; i < reg_items.size(); i++) {

        // If this holds, then we may trigger the forbidden pair
        if (((NondetDeadend*)(reg_items[i]))->op_index == op->nondet_index) {

            for (int j = 0; j < g_variable_name.size(); j++) {

                int val = (*(((NondetDeadend*)(reg_items[i]))->state))[j];

                // We may have broken it in a previous iteration
                if ((val != -1) &&
                    (val != (*state)[j]) &&
                    ((*state)[j] != -1))
                        break;

                // Just need to break one of the decisions
                if ((val != -1) &&
                    (val != (*s)[j])) {

                    assert((*state)[j] == -1);
                    (*state)[j] = (*s)[j];
                    break;

                }
            }
        }
    }
}

