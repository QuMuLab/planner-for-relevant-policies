#ifndef ONLINEHEURISTIC_H_
#define ONLINEHEURISTIC_H_

#include <vector>

#include "forks_abstraction.h"
#include "SP_heuristic.h"
#include "../problem.h"
#include "general_abstraction.h"
#include "var_projection.h"
#include "var_proj_mapping.h"
#include "mapping.h"
#include "domain_abstraction.h"

#include <iostream>

class Problem;

/*
 *      This class is intended for solving online without LP solver.
 *      Specifying cost partitioning allows to solve each ensemble member individually.
 */

class OnlineHeuristic: public SPHeuristic {
//	vector<SolutionMethod*> ensemble;

protected:
	int num_LP_vars(const State& state);

//	virtual SolutionMethod* add_binary_fork(Domain* abs_domain);
//	virtual SolutionMethod* add_bounded_inverted_fork(Domain* abs_domain);
	virtual SolutionMethod* add_pattern(vector<int>& pattern);

	virtual SolutionMethod* add_binary_fork(GeneralAbstraction* abs);
	virtual SolutionMethod* add_bounded_inverted_fork(GeneralAbstraction* abs);
	virtual SolutionMethod* add_pattern(GeneralAbstraction* abs);

	virtual SolutionMethod* add_binary_fork(ForksAbstraction* fork, Domain* abs_domain);
	virtual SolutionMethod* add_bounded_inverted_fork(IforksAbstraction* ifork, Domain* abs_domain);

public:
	OnlineHeuristic(bool use_cache=false);
	OnlineHeuristic(const Problem* prob, bool use_cache=false);
	virtual ~OnlineHeuristic();
	virtual void print_statistics() const {};

};

#endif /* ONLINEHEURISTIC_H_ */
