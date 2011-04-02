#ifdef USE_MOSEK
#include "init_opt_heuristic.h"
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

InitialOptimalHeuristic::InitialOptimalHeuristic(bool use_cache)
    : LPHeuristic(use_cache) {
}
InitialOptimalHeuristic::InitialOptimalHeuristic(const Problem* prob, bool use_cache)
    : LPHeuristic(prob,use_cache) {
}
InitialOptimalHeuristic::~InitialOptimalHeuristic() {
}

void InitialOptimalHeuristic::initialize() {
	LPHeuristic::initialize();
	int est_num_LP_vars = get_num_active_vars();
	cout << "Number LP vars :: " << est_num_LP_vars << endl;
	LP_MAX_TIME_BOUND = 60; // 1 minute bound on solver time
	if (est_num_LP_vars < MAX_LP_SIZE) {
//		cout << "------------->Start solving" << endl;
		int res =
			compute_Optimal_heuristic(*original_problem->get_initial_state());
		cout << "------------->End solving, solution value is " << res << endl;
	}
	int unsolved = get_number_of_unsolved_states();
	if ((est_num_LP_vars >= MAX_LP_SIZE) || (unsolved > 0)) {
		cout << "Unsolved LP in " << unsolved << " states" << endl;
		exit(1);
	}
	for (int ind=0;ind<get_ensemble_size();ind++) {
		if (STATISTICS >= 1) {
			get_ensemble_member(ind)->get_mapping()->get_abstract()->dump();
		}
//		get_ensemble_member(ind)->get_mapping()->get_abstract()->dump();
		//This part is a result of different number of d variables between online and offline versions
		if (get_ensemble_member(ind)->get_abstraction_type() == FORK) {
			get_ensemble_member(ind)->set_d_vars_multiplier(2);
			get_ensemble_member(ind)->set_default_number_of_variables();
		}
	}

	solve_all_and_remove_operators();
//	solve_all();
}

#endif
