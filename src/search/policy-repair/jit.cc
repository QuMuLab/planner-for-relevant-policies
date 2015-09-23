#include "jit.h"

void UnhandledState::dump() const {
    cout << "Unhandled State of distance " << cost << ":" << endl;
    state->dump_fdr();
}


bool perform_jit_repairs(Simulator *sim) {
    // The use of a stack is important for efficiency when using the optimized_scd.
    //  We close states closer to the end in the hope that strong cyclic reasoning
    //  will allow us to cease traversing the state space earlier, with a guarantee
    //  from the partial policy of partial states that a strong cyclic solution still
    //  exists.
    set<PartialState> * seen; // Keeps track of the full states we've seen
    stack<SCNode> * open_list; // Open list we traverse until strong cyclicity is proven
    vector<PartialState *> * created_states; // Used to clean up the created state objects

    PartialState * current_state; // The current step in the loop
    PartialState * previous_state; // The previous step in the loop (leading to the current_state)
    PartialState * current_goal; // The current goal in the loop
    const Operator * prev_op; // The last operator used to get us to current_state
    RegressionStep * prev_regstep; // The last RegressionStep that triggered prev_op
    bool made_change = false; // True if we add anything to the g_policy (i.e., replan)
    g_failed_open_states = 0; // Number of open states we couldn't solve (i.e., deadends)
    int num_checked_states = 0; // Number of states we check
    int num_fixed_states = 0; // Number of states we were able to repair (by replanning)
    int scd_skip_count = 0; // Number of times we checked a new state while having a dated SCD marking
    vector< DeadendTuple * > failed_states; // The failed states (used for creating deadends)
    const SCNode * current_node = NULL;

    bool warm_start = false; // Keep track if we've continued a search, or started from scratch

    bool debug_jic = false;

    // In case we have an initial policy, we run the optimized scd.
    if (g_optimized_scd) {
        g_policy->init_scd();
        made_change = true; // This becomes false again eventually
        while (made_change)
            made_change = g_policy->step_scd(failed_states, false);
    }

    // Back up the originial initial state
    PartialState *old_initial_state = new PartialState(g_initial_state());

    // Build the goal state
    PartialState *goal_orig = new PartialState();
    for (int i = 0; i < g_goal.size(); i++) {
        (*goal_orig)[g_goal[i].first] = g_goal[i].second;
    }

    if (debug_jic)
        cout << "\n\nStarting another JIC round." << endl;

    if (g_policy->seen) {
        cout << "Restoring the search from a previous epoch..." << endl;
        warm_start = true;
        seen = g_policy->seen;
        open_list = g_policy->open_list;
        created_states = g_policy->created_states;
    } else {
        seen = new set<PartialState>();
        open_list = new stack<SCNode>();
        created_states = new vector<PartialState *>();

        current_state = new PartialState(g_initial_state());
        current_goal = new PartialState(*goal_orig);
        open_list->push(SCNode(current_state, current_goal, NULL, NULL, NULL));

        created_states->push_back(current_state);
        created_states->push_back(current_goal);
    }

    if (debug_jic) {
        cout << "Starting JIC times: " << g_timer_jit() << " / " << g_jic_limit << endl;
        cout << "Starting states: " << open_list->size() << endl;
    }

    while (!open_list->empty() && ((g_timer_jit() < g_jic_limit) || g_record_relevant_pairs)) {
        num_checked_states++;
        current_state = open_list->top().full_state;
        previous_state = open_list->top().previous_state;
        current_goal = open_list->top().expected_state;
        prev_regstep = open_list->top().prev_regstep;
        prev_op = open_list->top().prev_op;
        current_node = &(open_list->top());
        open_list->pop();

        // If we are just going through states we know how to handle, give the SCD
        //  phase a chance to re-compute in case we skipped it previously.
        if (g_optimized_scd) {
            if (g_policy->opt_scd_skipped) {
                scd_skip_count++;
                if (scd_skip_count > 100) {
                    scd_skip_count = 0;
                    g_policy->init_scd(true);
                    bool _made_change = true;
                    while (_made_change)
                        _made_change = g_policy->step_scd(failed_states);
                }
            }
        }

        if (debug_jic) {
            cout << "\n\nChecking state:" << endl;
            current_state->dump_pddl();
        }

        if (0 == seen->count(*current_state)) {

            seen->insert(*current_state);

            // See if we can handle this state
            RegressionStep * regstep = g_policy->get_best_step(*current_state);

            bool have_solution = true;

            if (0 == regstep) {

                // We don't bother replanning if we are just recording the
                //  relevant pairs.
                if (g_record_relevant_pairs) {
                    have_solution = false;
                } else {

                    sim->set_state(current_state);
                    sim->set_goal(current_goal);
                    have_solution = sim->replan();

                    //
                    // As part of the recording process of solving the
                    //  problem, we probe reachable states for new deadends
                    //  and this may generate new forbidden state-action
                    //  pairs. As a result, this can invalidate the weak
                    //  plan we just constructed. So, we continually try to
                    //  find a weak plan such that the newly detected dead-
                    //  ends don't squash the weak plan right away.
                    //
                    // Note: Future parts of the weak plan may not work
                    //       the loop completes, but if that's the case
                    //       then we will necesarily replan when we reach
                    //       that state (the returned regstep will avoid
                    //       forbidden state-action pairs and so null is
                    //       returned if the weak plan no longer works).
                    //
                    while (have_solution && !(g_policy->get_best_step(*current_state)))
                        have_solution = sim->replan();


                    //
                    // With more advanced deadend detection, we iterate
                    //  the solving process to try and nab every combined
                    //  deadend possible. As long as new deadends are
                    //  created during search, we keep invoking the search
                    //  until it pulls things back to the initial state.
                    bool orig_have_solution = have_solution;
                    int unsolv_count = 1;
                    while (g_combine_deadends && !have_solution && g_replan_detected_deadends && (g_timer_jit() < g_jic_limit)) {
                        if (debug_jic)
                            cout << "Redoing the search to find more deadends (" << unsolv_count++ << ")." << endl;
                        have_solution = sim->replan();
                    }

                    assert(orig_have_solution == have_solution);
                    if (orig_have_solution != have_solution)
                        cout << "Error: A solvable problem became solvable!" << endl;

                    // regstep is now at the start of the newly found plan
                    regstep = g_policy->get_best_step(*current_state);

                    // Add the new goals to the sc condition for the previous reg step(s)
                    bool strengthened = false;
                    if (g_optimized_scd && prev_regstep && have_solution) {

                        // prev_state holds the info needed before the operator was taken
                        PartialState * prev_str_state = new PartialState(*(regstep->state), *prev_op, false, prev_regstep->state);
                        RegressionStep * prev_str_regstep = prev_regstep;
                        RegressionStep * str_regstep = regstep;
                        PartialState * updated = NULL;

                        bool repeating = true;
                        while(repeating) {

                            // We augment the state to include the stronger conditions
                            for (int i = 0; i < g_variable_name.size(); i++) {

                                // The regression through various outcomes should coincide
                                assert ((-1 == (*prev_str_state)[i]) ||
                                        (-1 == (*(prev_str_regstep->state))[i]) ||
                                        ((*prev_str_state)[i] == (*(prev_str_regstep->state))[i]));

                                if ((-1 != (*prev_str_state)[i]) &&
                                    (-1 == (*(prev_str_regstep->state))[i]))
                                {
                                    strengthened = true;
                                    if (!updated)
                                        updated = new PartialState(*(prev_str_regstep->state));
                                    (*updated)[i] = (*prev_str_state)[i];
                                }
                            }

                            if (updated) {

                                str_regstep = new RegressionStep(*(prev_str_regstep->op), updated, prev_str_regstep->distance, str_regstep, prev_str_regstep->prev);
                                str_regstep->next->prev = str_regstep;

                                g_policy->add_item(str_regstep);

                                if (debug_jic) {
                                    cout << "Adding strengthened step:" << endl;
                                    str_regstep->dump();
                                }

                                prev_str_regstep = str_regstep->prev;

                                delete prev_str_state;

                                if (prev_str_regstep)
                                    prev_str_state = new PartialState(*(str_regstep->state), *(prev_str_regstep->op), false, prev_str_regstep->state);

                                updated = NULL;

                                repeating = (g_repeat_strengthening && (prev_str_regstep != NULL));

                            } else
                                repeating = false;
                        }
                    }

                    // Since new policy has been added, we re-compute the sc detection
                    if (g_optimized_scd && have_solution) {
                        scd_skip_count = 0;
                        g_policy->init_scd(strengthened);
                        bool _made_change = true;
                        while (_made_change)
                            _made_change = g_policy->step_scd(failed_states);
                    }

                    if (have_solution) {
                        num_fixed_states++;
                        // We recompute the regstep here, just in case we need a better
                        //  strong cyclic one after the sc detection occurs.
                        regstep = g_policy->get_best_step(*current_state);
                        made_change = true;
                    }
                }
            }

            if (have_solution) {

                assert(regstep);

                if ( ! (regstep->is_goal || (g_optimized_scd && regstep->is_sc))) {
                    if (debug_jic)
                        cout << "\nNot marked..." << endl;
                    // Record the expected state
                    PartialState *full_expected_state = new PartialState(*current_state, *(regstep->op));
                    PartialState *expected_state = full_expected_state;
                    created_states->push_back(full_expected_state);

                    RegressionStep * expected_regstep = g_policy->get_best_step(*full_expected_state);

                    if (g_partial_planlocal && expected_regstep) {
                        expected_state = new PartialState(*(expected_regstep->state));
                        created_states->push_back(expected_state);
                    }

                    // Make sure that we aren't looping because of forbidden
                    //  state-action pairs (but have faith in our SCD!!)
                    if (expected_regstep && (!(expected_regstep->is_sc)) &&
                       (expected_regstep->distance >= regstep->distance)) {

                        // Setting g_updated_deadends to true will cause
                        //  the policy to be wiped and computed again with
                        //  the new set of FSAPs. This shouldn't create
                        //  a loop, as the only reason we would have a
                        //  monotonicity violation is because new FSAPs
                        //  are prohibiting the use of previously computed
                        //  "best_step"'s as the expected_regstep.

                        if (debug_jic)
                            cout << "Found a monotonicity violation." << endl;

                        g_monotonicity_violations++;
                        g_updated_deadends = true;
                    }

                    for (int i = 0; i < g_nondet_mapping[regstep->op->nondet_index]->size(); i++) {
                        PartialState *new_state = new PartialState(*current_state, *((*(g_nondet_mapping[regstep->op->nondet_index]))[i]));
                        created_states->push_back(new_state);

                        if (0 == seen->count(*new_state)) {
                            open_list->push(SCNode(new_state, expected_state, current_state, regstep, (*(g_nondet_mapping[regstep->op->nondet_index]))[i]));
                            if (debug_jic) {
                                cout << "\nAdding new state:" << endl;
                                new_state->dump_pddl();
                            }
                        }
                    }
                    // We add this one extra time to ensure a DFS traversal of the
                    //  state space when looking for a strong cyclic solution. This
                    //  introduces a duplicate, but the outer if statement catches
                    //  this just fine, and the memory hit is negligible.
                    open_list->push(SCNode(full_expected_state, expected_state, current_state, regstep, regstep->op));
                } else {
                    if (debug_jic) {
                        cout << "\nMarked..." << endl;
                    }
                }

                if (debug_jic)
                    cout << "\nState handled..." << endl;

            } else if (!g_record_relevant_pairs) { // Skip the deadend handling if we're just checking what's relevant

                if (debug_jic)
                    cout << "\nState failed..." << endl;

                g_failed_open_states++;

                // This only matches when no strong cyclic solution exists
                if (*current_state == *old_initial_state) {
                    if (g_detect_deadends)
                        g_failed_open_states = failed_states.size();

                    if (!g_silent_planning) {
                        cout << "Found the initial state to be a failed one. No strong cyclic plan exists." << endl;
                        cout << "Using the best policy found, with a score of " << g_best_policy_score << endl;
                    }
                    g_state_registry->reset_initial_state();
                    for (int i = 0; i < g_variable_name.size(); i++)
                        g_initial_state_data[i] = (*old_initial_state)[i];
                    sim->set_state(old_initial_state);
                    sim->set_goal(goal_orig);

                    // Use the best policy we've found so far
                    if (g_best_policy != g_policy)
                        delete g_policy;
                    g_policy = g_best_policy;

                    if (g_timer_jit() < g_jic_limit)
                        g_policy->mark_complete();

                    // Clean up the states we've created
                    for (int i = 0; i < created_states->size(); i++) {
                        if ((*created_states)[i])
                            delete (*created_states)[i];
                    }

                    // Return false so jic stops
                    return false;
                } else {
                    if (g_detect_deadends) {
                        bool generalized = true;
                        if (g_generalize_deadends)
                            generalized = generalize_deadend(*current_state);

                        assert (NULL != current_state);
                        assert (NULL != previous_state);
                        assert (NULL != prev_op);

                        if (debug_jic && !generalized)
                            cout << "Is it really not a deadend? " << is_deadend(*current_state) << endl;;

                        failed_states.push_back(new DeadendTuple(current_state, previous_state, prev_op));
                    }
                }
            }
        } else {
            if (debug_jic) {
                cout << "\nState seen..." << endl;
            }
        }
    }

    bool finished_early = (g_jic_limit <= g_timer_jit());
    if (debug_jic) {
        cout << "Remaining states: " << open_list->size() << endl;
        cout << "Ending JIC times: " << g_timer_jit() << " / " << g_jic_limit << endl;
    }

    // We need to update the value since some may have been added to the
    //  list during optimized_scd
    if (g_detect_deadends)
        g_failed_open_states = failed_states.size();

    // Reset the original goal and initial state
    g_state_registry->reset_initial_state();
    for (int i = 0; i < g_variable_name.size(); i++)
        g_initial_state_data[i] = (*old_initial_state)[i];
    sim->set_state(old_initial_state);
    sim->set_goal(goal_orig);

    // Short circuit early if we're just recording what's relevant
    if (g_record_relevant_pairs) {
        // Clean up the states we've created
        for (int i = 0; i < created_states->size(); i++) {
            if ((*created_states)[i])
                delete (*created_states)[i];
        }
        return false;
    }

    cout << "\nCould not close " << g_failed_open_states << " of " << num_fixed_states + g_failed_open_states << " open leaf states." << endl;
    cout << "Investigated " << num_checked_states << " states for the strong cyclic plan." << endl;

    // If we closed every open state, then the policy must be strongly cyclic.
    if ((0 == g_failed_open_states) && (g_timer_jit() < g_jic_limit) &&
        !made_change && !g_updated_deadends && !warm_start)
    {
        g_policy->mark_strong();
        cout << "Marking policy strong cyclic." << endl;
    }

    if (made_change || (g_failed_open_states > 0) || g_updated_deadends || g_policy->is_strong_cyclic()) {

        double cur_score = g_policy->get_score();

        if (g_policy->better_than(g_best_policy)) {

            cout << "Found a better policy of score " << cur_score << endl;

            if (g_best_policy && (g_best_policy != g_policy))
                delete g_best_policy;

            g_best_policy_score = cur_score;
            g_best_policy = g_policy;

        } else {
            cout << "Went through another policy of score " << cur_score << endl;
        }

    }

    if (g_detect_deadends && ((g_failed_open_states > 0) || g_updated_deadends) && (g_timer_jit() < g_jic_limit)) {
        update_deadends(failed_states);
        g_updated_deadends = false;

        // We delete the policy so we can start from scratch next time with
        //  the deadends recorded.
        if (g_best_policy != g_policy)
            delete g_policy;
        g_policy = new Policy();

        made_change = true;
    }

    // Store the jic rollout in case we want to pick the search up in the
    //  next epoch or final fsap-free round
    if (finished_early && (g_failed_open_states == 0) && !g_updated_deadends) {
        // Add the most recent SCNode in case we start up another epoch
        if (current_node)
            open_list->push(*current_node);

        cout << "Saving the jic search state." << endl;
        g_policy->seen = seen;
        g_policy->open_list = open_list;
        g_policy->created_states = created_states;

    } else {

        // Clean up the data structures we've created
        for (int i = 0; i < created_states->size(); i++) {
            if ((*created_states)[i])
                delete (*created_states)[i];
        }
        delete seen;
        delete open_list;
        delete created_states;

        if (warm_start) {
            g_policy->seen = NULL;
            g_policy->open_list = NULL;
            g_policy->created_states = NULL;
        }
    }

    return made_change;
}
