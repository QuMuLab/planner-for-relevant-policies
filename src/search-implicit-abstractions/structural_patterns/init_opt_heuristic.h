#ifndef INITOPTHEURISTIC_H_
#define INITOPTHEURISTIC_H_

#ifdef USE_MOSEK
#include <vector>
#include "SP_globals.h"
#include "forks_abstraction.h"
#include "LP_heuristic.h"
#include "../problem.h"
#include "general_abstraction.h"
#include "var_projection.h"
#include "var_proj_mapping.h"
#include "mapping.h"
#include "domain_abstraction.h"

#include <iostream>

class Problem;

class InitialOptimalHeuristic: public LPHeuristic {

protected:
	int num_LP_vars(const State& state);

public:
	InitialOptimalHeuristic(bool use_cache=false);
	InitialOptimalHeuristic(const Problem* prob, bool use_cache=false);
	virtual ~InitialOptimalHeuristic();

    virtual void initialize();
	virtual int compute_heuristic(const State& state) { return SPHeuristic::compute_heuristic(state);}

};

#endif
#endif /* INITOPTHEURISTIC_H_ */
