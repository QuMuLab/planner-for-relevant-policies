#ifndef LP_BINARY_FORK_GEN_H_
#define LP_BINARY_FORK_GEN_H_

#include "binary_forks_gen.h"
#include <cfloat>

/* This class describes LP construction for forks with binary root domain as suggested
 * in the paper Optimal Additive Composition of Abstraction-based Admissible Heuristics.
 */

class LPBinaryFork: public BinaryFork {

	virtual LPConstraint* set_h_constraint(int sigma, const state_var_t * eval_state) const;
protected:
	vector<LPConstraint*> dynamic_LPConstraints[2];

public:
	LPBinaryFork();
	LPBinaryFork(GeneralAbstraction* abs);
	LPBinaryFork(ForksAbstraction* f, Domain* abs_domain);
	virtual ~LPBinaryFork();

	virtual void initiate();
	virtual void set_static_constraints();
	virtual void get_dynamic_constraints(const State* state, vector<LPConstraint*>& dyn_constr);
	virtual int w_var(Operator* a) const;

	virtual void remove_abstract_operators() {}
	virtual void free_constraints();

};

#endif /* LP_BINARY_FORK_GEN_H_ */
