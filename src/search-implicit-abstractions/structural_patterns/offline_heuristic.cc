#include "offline_heuristic.h"
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
//#include "LPConstraint.h"


OfflineHeuristic::OfflineHeuristic(bool use_cache)
    : SPHeuristic(use_cache) {
	lph = NULL;
}
OfflineHeuristic::OfflineHeuristic(const Problem* prob, bool use_cache)
    : SPHeuristic(prob,use_cache) {
	lph = NULL;
}


OfflineHeuristic::~OfflineHeuristic() {
//	if (lph)
//		delete lph;
}


void OfflineHeuristic::initialize() {

	if (get_cost_partitioning_strategy() == INITIAL_OPTIMAL) {
#ifdef USE_MOSEK
   		cout << "------------->Starting" << endl;
		lph = new LPHeuristic(original_problem);
   		lph->set_strategy(get_strategy());
   		lph->set_percentage_of_ensemble(get_percentage_of_ensemble());
   		lph->set_minimal_size_for_non_projection_pattern(get_minimal_size_for_non_projection_pattern());
   		lph->set_cost_partitioning_strategy(GENERAL);
   		lph->create_ensemble();
		// print statistics
		cout << "SAS variables :: " << original_problem->get_vars_number() << endl;
		cout << "Ensemble size :: " << lph->get_ensemble_size() << endl;
   	   	lph->initialize();
   		int est_num_LP_vars = lph->get_num_active_vars();
   		cout << "Number LP vars :: " << est_num_LP_vars << endl;
//		if (STATISTICS >= 1) {
//			cout << "LP for initial state with approximately "<< est_num_LP_vars <<" variables is created" << endl;
//		}
		LP_MAX_TIME_BOUND = 60; // 1 minute bound on solver time
   		if (est_num_LP_vars < MAX_LP_SIZE) {
   	   		cout << "------------->Start solving" << endl;
   			lph->compute_heuristic(*original_problem->get_initial_state());
   	   		cout << "------------->End solving" << endl;
   		}
   		int unsolved = lph->get_number_of_unsolved_states();
   		if ((est_num_LP_vars >= MAX_LP_SIZE) || (unsolved > 0)) {
    		cout << "Unsolved LP in " << unsolved << " states" << endl;
    		exit(1);
   		}
   		set_ensemble();
   		if ((est_num_LP_vars >= MAX_LP_SIZE) || (unsolved > 0)) {
    		set_uniform_representatives_cost();
   		}
   		//delete lph;
#else
		cout << "No LP Solver defined in this version" << endl;
		exit(1);
#endif

	}

	SPHeuristic::initialize();
}


void OfflineHeuristic::set_ensemble() {
#ifdef USE_MOSEK
	assert(0 == get_ensemble_size());
	for (int ind=0; ind < lph->get_ensemble_size(); ind++) {
		SolutionMethod* membr = lph->get_ensemble_member(ind);
		if (!membr->is_active())
			continue;
		if (membr->get_abstraction_type() == FORK) {
			add_ensemble_member(add_binary_fork(membr->get_abstraction()));
		} else if (membr->get_abstraction_type() == INVERTED_FORK) {
			add_ensemble_member(add_bounded_inverted_fork(membr->get_abstraction()));
		} else if (membr->get_abstraction_type() == PATTERN) {
			add_ensemble_member(add_pattern(membr->get_abstraction()));
		}
	}
	cout << "Done setting the ensemble" << endl;
#else
		cout << "No LP Solver defined in this version" << endl;
		exit(1);
#endif
}

/////////////////////////////////////////////////////////////////////////////////
SolutionMethod* OfflineHeuristic::add_binary_fork(GeneralAbstraction* abs) {
	return new BinaryFork(abs);
}

SolutionMethod* OfflineHeuristic::add_bounded_inverted_fork(GeneralAbstraction* abs) {
	return new BoundedIfork(abs);
}

SolutionMethod* OfflineHeuristic::add_pattern(GeneralAbstraction* abs) {
	return new Projection(abs);
}
/////////////////////////////////////////////////////////////////////////////////
// Creating multiple domain abstraction using the same base abstraction
SolutionMethod* OfflineHeuristic::add_binary_fork(ForksAbstraction* fork, Domain* abs_domain) {
	return new BinaryFork(fork, abs_domain);
}

SolutionMethod* OfflineHeuristic::add_bounded_inverted_fork(IforksAbstraction* ifork, Domain* abs_domain) {
	return new BoundedIfork(ifork, abs_domain);
}

/////////////////////////////////////////////////////////////////////////////////

/*
SolutionMethod* OfflineHeuristic::add_binary_fork(Domain* abs_domain) {
	BinaryFork* bf = new BinaryFork();
	bf->set_root_var_and_domain(abs_domain);
	bf->create(original_problem);
	bf->set_abstraction_type(FORK);
	return bf;
}

SolutionMethod* OfflineHeuristic::add_bounded_inverted_fork(Domain* abs_domain) {
	BoundedIfork* bif = new BoundedIfork();
	bif->set_root_var_and_domain(abs_domain);
	bif->create(original_problem);
	bif->set_abstraction_type(INVERTED_FORK);
	return bif;
}
*/
SolutionMethod* OfflineHeuristic::add_pattern(vector<int>& pattern) {
	Projection* ptrn = new Projection(pattern);
	ptrn->create(original_problem);
	ptrn->set_abstraction_type(PATTERN);
	return ptrn;
}


