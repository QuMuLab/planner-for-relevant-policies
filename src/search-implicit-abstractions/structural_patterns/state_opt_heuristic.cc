//#ifdef USE_MOSEK
#ifdef USE_LP

#include "state_opt_heuristic.h"
#include "var_projection.h"
#include <vector>
#include "../problem.h"
#include "../globals.h"
#include "general_abstraction.h"
#include "var_proj_mapping.h"
#include <iostream>
#include "projection_gen.h"
#include "binary_forks_gen.h"
#include "bounded_iforks_gen.h"
#include "LP_heuristic.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "../causal_graph.h"

StateOptimalHeuristic::StateOptimalHeuristic(const State& state, bool use_cache)
    : LPHeuristic(use_cache),eval_state(state) {
}
StateOptimalHeuristic::StateOptimalHeuristic(const State& state, const Problem* prob, bool use_cache)
    : LPHeuristic(prob,use_cache),eval_state(state) {
}
StateOptimalHeuristic::~StateOptimalHeuristic() {
}

void StateOptimalHeuristic::initialize() {
	if (original_problem->is_goal(&eval_state)) {
		cout << "Cannot create optimal partition for goal state!" << endl;
		exit(1);
	}
//	eval_state.dump();
	LPHeuristic::initialize();

	// Solving LP only if the number of LP variables is less than the bound set.
//	int est_num_LP_vars = get_num_active_vars();
//	cout << "Number LP vars :: " << est_num_LP_vars << ", Bound :: " << MAX_LP_SIZE << endl;
//	if (est_num_LP_vars >= MAX_LP_SIZE) {
//		exit(1);
//	}
	LP_MAX_TIME_BOUND = 300; // 5 minute bound on solver time
	cout << "------------->Start solving" << endl;
	int res =
		compute_Optimal_heuristic(eval_state);
	cout << "------------->End solving, solution value is " << res << endl;

	if (get_number_of_unsolved_states() > 0) { // If unsolved within the bound
		cout << "Unsolved LP for the given state:" << endl;
		eval_state.dump();
		exit(1);
	}
	for (int ind=0;ind<get_ensemble_size();ind++) {
		if (STATISTICS >= 1) {
			get_ensemble_member(ind)->get_mapping()->get_abstract()->dump();
		}
		//This part is a result of different number of d variables between online and offline versions
		if (get_ensemble_member(ind)->get_abstraction_type() == FORK) {
			get_ensemble_member(ind)->set_d_vars_multiplier(2);
			get_ensemble_member(ind)->set_default_number_of_variables();
		}
		get_ensemble_member(ind)->free_constraints();
	}

	check_cost_partition();

	solve_all_and_remove_operators();
//	solve_all();
}

#endif
