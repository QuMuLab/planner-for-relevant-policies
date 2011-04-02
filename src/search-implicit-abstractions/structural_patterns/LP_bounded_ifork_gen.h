#ifndef LP_BOUNDED_IFORK_GEN_H_
#define LP_BOUNDED_IFORK_GEN_H_

#include "bounded_iforks_gen.h"
#include "bounded_iforks.h"
#include <cfloat>
#include "ifork_root_path.h"

/* This class describes LP construction for inverted forks with bounded root domain as suggested
 * in the paper Optimal Additive Composition of Abstraction-based Admissible Heuristics.
 */

class LPBoundedIfork: public BoundedIfork {
private:
	void precalculate_path(IforkRootPath* path);

public:
	LPBoundedIfork();
	LPBoundedIfork(GeneralAbstraction* abs);
	LPBoundedIfork(IforksAbstraction* ifork, Domain* abs_domain);
	virtual ~LPBoundedIfork();

	virtual void set_static_constraints();

	virtual void initiate();

	virtual void get_dynamic_constraints(const State* state, vector<LPConstraint*>& dyn_constr);

	virtual int h_var() const;
	virtual int w_var(Operator* a) const;

	virtual void remove_abstract_operators() {}

};

#endif /* LP_BOUNDED_IFORK_GEN_H_ */
