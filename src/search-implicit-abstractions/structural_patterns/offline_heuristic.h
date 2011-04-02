#ifndef OFFLINEHEURISTIC_H_
#define OFFLINEHEURISTIC_H_

#include <vector>
#include "SP_globals.h"
#include "forks_abstraction.h"
#include "SP_heuristic.h"
#include "LP_heuristic.h"
#include "../problem.h"
#include "general_abstraction.h"
#include "var_projection.h"
#include "var_proj_mapping.h"
#include "mapping.h"
#include "domain_abstraction.h"

#include <iostream>


class Problem;
class LPHeuristic;

class OfflineHeuristic: public SPHeuristic {

	LPHeuristic* lph;
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
	OfflineHeuristic(bool use_cache=false);
	OfflineHeuristic(const Problem* prob, bool use_cache=false);
	virtual ~OfflineHeuristic();

    virtual void initialize();
	virtual void set_ensemble();
	virtual void print_statistics() const { };

//	const vector<SolutionMethod*> &get_ensemble() const {return ensemble;};
};

#endif /* OFFLINEHEURISTIC_H_ */
