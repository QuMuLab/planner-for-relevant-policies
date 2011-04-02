#ifndef BOUNDED_IFORKS_ON_H_
#define BOUNDED_IFORKS_ON_H_

#include "bounded_iforks.h"
#include "bounded_iforks_gen.h"
#include <cfloat>
#include "ifork_root_path.h"

/* This class describes LP construction for inverted forks with bounded root domain as suggested
 * in the paper Optimal Additive Composition of Abstraction-based Admissible Heuristics.
 */

class BoundedIforks_ON: public BoundedIfork {

public:
	BoundedIforks_ON();
	BoundedIforks_ON(GeneralAbstraction* abs);
	BoundedIforks_ON(IforksAbstraction* ifork, Domain* abs_domain);
	virtual ~BoundedIforks_ON();

	virtual void solve() {}

	virtual double get_solution_value(const State* state) {
		solve_internal(false);  //Solving
		return BoundedIfork::get_solution_value(state);
	}
	virtual void remove_abstract_operators() {}

};

#endif /* BOUNDED_IFORKS_ON_H_ */
