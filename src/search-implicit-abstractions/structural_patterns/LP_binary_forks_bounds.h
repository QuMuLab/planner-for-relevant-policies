#ifndef LP_BINARY_FORKS_BOUNDS_H_
#define LP_BINARY_FORKS_BOUNDS_H_

#include "LP_binary_fork_gen.h"
#include "binary_forks.h"
#include "binary_forks_on.h"
#include <cfloat>

/* This class describes LP construction for forks with binary root domain as suggested
 * in the paper Optimal Additive Composition of Abstraction-based Admissible Heuristics.
 */

class LPBinaryForks_b: public LPBinaryFork {
	virtual LPConstraint* set_h_constraint(int sigma, const state_var_t * eval_state) const;
public:
	LPBinaryForks_b();
	LPBinaryForks_b(GeneralAbstraction* abs);
	LPBinaryForks_b(ForksAbstraction* f, Domain* abs_domain);
	virtual ~LPBinaryForks_b();

	virtual void initiate();
	virtual void set_static_constraints();
	virtual void get_dynamic_constraints(const State* state, vector<LPConstraint*>& dyn_constr);

	LPConstraint* set_h_constraint(int sigma, int root_zero, bool tokeep) const;
	LPConstraint* set_p_constraint(int v, int val, int pre, int post, int prv, int w_ind, bool tokeep) const;
	LPConstraint* set_d_constraint(int v, int val_0, int val_1, int sz, int root_zero, bool tokeep) const;

	virtual int w_v(int var, int val1, int val2, int root_val) const;

	void set_bounds_for_state(const State* state);
	void set_general_bounds();
	int get_domain_bound(int v, int g_v, int root_zero) const;
	int get_domain_bound(int v, int g_v, const state_var_t * eval_state) const;

};

#endif /* LP_BINARY_FORKS_BOUNDS_H_ */
