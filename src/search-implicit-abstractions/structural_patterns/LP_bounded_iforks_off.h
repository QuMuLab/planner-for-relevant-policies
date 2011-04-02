#ifndef LP_BOUNDED_IFORKS_OFF_H_
#define LP_BOUNDED_IFORKS_OFF_H_

#include "LP_bounded_ifork_gen.h"
#include "bounded_iforks.h"
#include <cfloat>
#include "ifork_root_path.h"

/* This class describes LP construction for inverted forks with bounded root domain as suggested
 * in the paper Optimal Additive Composition of Abstraction-based Admissible Heuristics.
 */


class LPBoundedIforks_OFF: public LPBoundedIfork {

//private:
//	double calculate_supp_cost(int v, vector<int>& supp);
//	void precalculate_path(IforkRootPath* path);

public:
	LPBoundedIforks_OFF();
	LPBoundedIforks_OFF(GeneralAbstraction* abs);
	LPBoundedIforks_OFF(IforksAbstraction* ifork, Domain* abs_domain);
	virtual ~LPBoundedIforks_OFF();

//	void initiate();
	virtual void set_objective();
	virtual void set_static_constraints();
	virtual void get_dynamic_constraints(const State*, vector<LPConstraint*>& ) {exit(1);}
	virtual void solve() { solve_internal(false);}

//	virtual double get_solution_value(const State* state);

//	virtual void set_solution(Solution* sol);


};

#endif /* LP_BOUNDED_IFORKS_OFF_H_ */
