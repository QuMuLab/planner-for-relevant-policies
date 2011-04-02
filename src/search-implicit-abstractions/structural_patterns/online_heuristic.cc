#include "SP_globals.h"
#include "online_heuristic.h"
#include "var_projection.h"
#include <vector>
#include "../problem.h"
#include "../globals.h"
#include "general_abstraction.h"
#include "var_proj_mapping.h"
#include <iostream>
#include "projection_on.h"
#include "binary_forks_on.h"
#include "bounded_iforks_on.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "../causal_graph.h"
//#include "LPConstraint.h"


OnlineHeuristic::OnlineHeuristic(bool use_cache)
    : SPHeuristic(use_cache) {
//	original_problem = new Problem();

}

OnlineHeuristic::OnlineHeuristic(const Problem* prob, bool use_cache)
    : SPHeuristic(prob,use_cache) {
}


OnlineHeuristic::~OnlineHeuristic() {
}

///////////////////////////////////////////////////////////////////////////////
/*
void OnlineHeuristic::initialize() {

//	if (STATISTICS >= 1) {
//		original_problem->dump();
//	}
	create_ensemble();
	// print statistics
	cout << "SAS variables :: " << original_problem->get_vars_number() << endl;
	cout << "Ensemble size :: " << ensemble.size() << endl;

	// Setting the cost partitioning
	set_uniform_representatives_cost();

	int ens_size = ensemble.size();
	int ens_types[3] = {};
	for (int ind=0;ind<ens_size;ind++) {
//		if (STATISTICS >= 1) {
//			cout << "Ensemble member "<< ind << endl;
//			ensemble[ind]->get_mapping()->get_abstract()->dump();
//		}
		ensemble[ind]->initiate();
//		ensemble[ind]->solve();
		ens_types[ensemble[ind]->get_abstraction_type()]++;
	}

	cout << "*Forks* in Ensemble :: " << ens_types[0] << endl;
	cout << "*Inverted Forks* in Ensemble :: " << ens_types[1] << endl;
	cout << "*Projections* in Ensemble :: " << ens_types[2] << endl;

}
*/

SolutionMethod* OnlineHeuristic::add_binary_fork(GeneralAbstraction* abs) {
	return new BinaryForks_ON(abs);
}

SolutionMethod* OnlineHeuristic::add_bounded_inverted_fork(GeneralAbstraction* abs) {
	return new BoundedIforks_ON(abs);
}

SolutionMethod* OnlineHeuristic::add_pattern(GeneralAbstraction* abs) {
	return new Projection_ON(abs);
}

/////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////
// Creating multiple domain abstraction using the same base abstraction
SolutionMethod* OnlineHeuristic::add_binary_fork(ForksAbstraction* fork, Domain* abs_domain) {
	return new BinaryForks_ON(fork, abs_domain);
}

SolutionMethod* OnlineHeuristic::add_bounded_inverted_fork(IforksAbstraction* ifork, Domain* abs_domain) {
	return new BoundedIforks_ON(ifork, abs_domain);
}

/////////////////////////////////////////////////////////////////////////////////

/*
SolutionMethod* OnlineHeuristic::add_binary_fork(Domain* abs_domain) {
	BinaryForks_ON* bf = new BinaryForks_ON();
	bf->set_root_var_and_domain(abs_domain);
	bf->create(original_problem);
	bf->set_abstraction_type(FORK);
	return bf;
}

SolutionMethod* OnlineHeuristic::add_bounded_inverted_fork(Domain* abs_domain) {
	BoundedIforks_ON* bif = new BoundedIforks_ON();
	bif->set_root_var_and_domain(abs_domain);
	bif->create(original_problem);
	bif->set_abstraction_type(INVERTED_FORK);
	return bif;
}
*/

SolutionMethod* OnlineHeuristic::add_pattern(vector<int>& pattern) {
	Projection_ON* ptrn = new Projection_ON(pattern);
	ptrn->create(original_problem);
	ptrn->set_abstraction_type(PATTERN);
	return ptrn;
}

//////////////////////////////////////////////////////////////////////////////////
