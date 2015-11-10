#include "deadend.h"


bool is_deadend(PartialState &state) {

    // We must always set up the forbidden operators. Why? Well when we
    //  aren't checking with forbidden operators, they are always removed
    //  from the relaxed reachability -- this may create incorrect deadends
    //  but that's fine as we'll reset everything if we don't stumble on
    //  a strong cyclic solution. If we /are/ using forbidden operators
    //  in the computation, it still prunes those that aren't applicable
    //  now, and have no chance of becoming applicable.
    ((AdditiveHeuristic *)g_heuristic_for_reachability)->compute_forbidden(state);
    ((AdditiveHeuristic *)g_heuristic_for_reachability)->reset();
    return (-1 == ((AdditiveHeuristic *)g_heuristic_for_reachability)->compute_add_and_ff(state));
}


bool generalize_deadend(PartialState &state) {

    bool debug = false;

    // If the whole state isn't recognized as a deadend, then don't bother
    //  looking for a subset of the state
    if (!is_deadend(state))
        return false;

    // We go through each variable and unset it, checking if the relaxed reachability
    //  is violated.
    for (int i = 0; i < g_variable_name.size(); i++) {

        int old_val = state[i];
        state[i] = -1;

        // If relaxing variable i causes us to reach the goal, keep it in
        if (!is_deadend(state))
            state[i] = old_val;
    }

    if (debug) {
        cout << "Found relaxed deadend:" << endl;
        state.dump_pddl();
    }

    return true;
}

void update_deadends(vector< DeadendTuple* > &failed_states) {

    list<PolicyItem *> de_items;
    list<PolicyItem *> de_states;

    bool debug = false;

    PartialState * dummy_state = new PartialState();

    for (int i = 0; i < failed_states.size(); i++) {

        // Generalize the deadend if need be
        PartialState * failed_state = failed_states[i]->de_state;
        PartialState * failed_state_prev = failed_states[i]->prev_state;
        const Operator * prev_op = failed_states[i]->prev_op;

        if (debug) {
            cout << "\n(#" << g_debug_count++ << ") Creating forbidden state-action pairs for deadend:" << endl;
            failed_state->dump_pddl();
            cout << endl;
        }

        // Add the failed state to our list of deadends
        de_states.push_back(new NondetDeadend(new PartialState(*failed_state)));

        // HAZ: Only do the forbidden state-action computation when
        //  the non-deterministic action doesn't have any associated
        //  conditional effects. This is ensured by the construction
        //  of the g_regressable_ops data structure.

        // Get the regressable operators for the given state.
        vector<PolicyItem *> reg_items;
        g_regressable_ops->generate_applicable_items(*failed_state, reg_items, true, g_regress_only_relevant_deadends);

        // For each operator, create a new deadend avoidance pair
        for (int j = 0; j < reg_items.size(); j++) {

            RegressableOperator *ro = (RegressableOperator*)(reg_items[j]);

            de_items.push_back(new NondetDeadend(new PartialState(*failed_state, *(ro->op), false, dummy_state),
                                                     ro->op->nondet_index));
            if (debug) {
                cout << "Creating new forbidden state-action pair:" << endl;
                de_items.back()->dump();
            }
        }

        ////////////////////////////////////////////

        // Check to see if we have any consistent "all-fire" operators
        reg_items.clear();
        g_regressable_cond_ops->generate_applicable_items(*failed_state, reg_items, true, g_regress_only_relevant_deadends);

        // For each operator, create a new deadend avoidance pair
        for (int j = 0; j < reg_items.size(); j++) {

            RegressableOperator *ro = (RegressableOperator*)(reg_items[j]);

            de_items.push_back(new NondetDeadend(
                                    new PartialState(*failed_state, *(ro->op), false, ro->op->all_fire_context),
                                    ro->op->nondet_index));

            if (debug) {
                cout << "Creating new (all-fire) forbidden state-action pair:" << endl;
                de_items.back()->dump();
            }
        }

        ////////////////////////////////////////////

        // If we have a specified previous state and action, use that to
        //  build a forbidden state-action pair
        if (NULL != failed_state_prev) {
            de_items.push_back(new NondetDeadend(
                    new PartialState(*failed_state, *prev_op, false, failed_state_prev),
                    prev_op->nondet_index));

            if (debug) {
                cout << "Creating new (default) forbidden state-action pair:" << endl;
                de_items.back()->dump();
            }
        }
    }

    delete dummy_state;

    g_deadend_policy->update_policy(de_items);
    g_deadend_states->update_policy(de_states);

    if (g_repeat_fsap_backwards) {
        for (std::list<PolicyItem *>::iterator it=de_items.begin(); it != de_items.end(); ++it) {

            // Make sure the partial state isn't already a deadend
            if (!(g_deadend_states->check_match(*((*it)->state), false))) {

                // Just call the successor generator to see if the combination is triggered
                vector<const Operator *> ops;
                g_successor_generator->generate_applicable_ops(*((*it)->state), ops);
                if (ops.size() == 0)
                    g_repeat_fsap_count++;
            }

        }
    }
}


void DeadendAwareSuccessorGenerator::generate_applicable_ops(const StateInterface &_curr, vector<const Operator *> &ops) {
    if (g_detect_deadends && g_deadend_policy) {

        PartialState curr = PartialState(_curr);

        bool debug = false;

        if (debug)
            cout << "\nRunning the deadend aware successor generator..." << endl;

        vector<PolicyItem *> reg_items;
        vector<const Operator *> orig_ops;
        map<int, PolicyItem *> fsap_map;

        g_successor_generator_orig->generate_applicable_ops(_curr, orig_ops, true);
        g_deadend_policy->generate_applicable_items(curr, reg_items, false, false);

        set<int> forbidden;
        for (int i = 0; i < reg_items.size(); i++) {

            int index = ((NondetDeadend*)(reg_items[i]))->op_index;

            forbidden.insert(index);

            if ((fsap_map.find(index) == fsap_map.end()) ||
                (reg_items[i]->state->size() < fsap_map[index]->state->size()))
                    fsap_map[index] = reg_items[i];
        }

        vector<int> ruled_out;
        for (int i = 0; i < orig_ops.size(); i++) {
            if (0 == forbidden.count(orig_ops[i]->nondet_index)) {
                if (debug)
                    cout << "Allowing operator " << orig_ops[i]->get_name() << endl;
                ops.push_back(orig_ops[i]);
            }
            else {

                if (g_combine_deadends)
                    ruled_out.push_back(orig_ops[i]->nondet_index);

                /* HAZ: Since we are using the ff heuristic with preferred operators,
                 *      we don't want the preferred operators to sneak into the applicable
                 *      list of actions. As such, we "mark" the operator which prevents
                 *      the operator from being added. See LazySearch::get_successor_operators
                 *      for where this occurrs.
                 */
                orig_ops[i]->mark();

                if (debug)
                    cout << "Forbidding operator " << orig_ops[i]->get_name() << endl;
            }
        }

        // Add this state as a deadend if we have ruled out everything
        if (!g_limit_states && g_record_online_deadends &&
             g_combine_deadends && (orig_ops.size() > 0) && ops.empty()) {

            PartialState *newDE = new PartialState();
            for (int i = 0; i < ruled_out.size(); i++) {
                newDE->combine_with(*(((NondetDeadend*)(fsap_map[ruled_out[i]]))->state));
            }

            if (debug) {
                cout << "<< (#" << g_debug_count++ << ") Found a new deadend state of size " << newDE->size() << " >>" << endl;
                newDE->dump_pddl();
            }

            g_combined_count++;

            vector<DeadendTuple *> failed_states;
            failed_states.push_back(new DeadendTuple(newDE, NULL, NULL));
            g_updated_deadends = true;
            update_deadends(failed_states);
        }

    } else {

        g_successor_generator_orig->generate_applicable_ops(_curr, ops, true);

    }
    return;
}


bool sample_for_depth1_deadends(const SearchEngine::Plan &plan, PartialState *state) {

    bool debug = false;

    if (!g_detect_deadends)
        return false;

    vector<DeadendTuple *> new_deadends;
    PartialState* old_s = state;
    PartialState* new_s;

    for (int i = 0; i < plan.size(); i++) {
        for (int j = 0; j < g_nondet_mapping[plan[i]->nondet_index]->size(); j++) {
            PartialState *succ_state = new PartialState(*old_s, *((*(g_nondet_mapping[plan[i]->nondet_index]))[j]));
            if (is_deadend(*succ_state)) {
                if (g_generalize_deadends)
                    generalize_deadend(*succ_state);
                new_deadends.push_back(new DeadendTuple(succ_state, new PartialState(*old_s), (*(g_nondet_mapping[plan[i]->nondet_index]))[j]));
            }
        }

        new_s = new PartialState(*old_s, *plan[i]);
        delete old_s;
        old_s = new_s;
    }

    if (new_deadends.size() > 0) {
        if (debug)
            cout << "Found " << new_deadends.size() << " new deadends!" << endl;
        g_updated_deadends = true;
        update_deadends(new_deadends);
        return true;
    }

    return false;
}

