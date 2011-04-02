#ifndef LP_BINARY_FORKS_KD_H_
#define LP_BINARY_FORKS_KD_H_

#include "LP_binary_fork_gen.h"
#include "binary_forks.h"
#include <cfloat>

/* This class describes LP construction for forks with binary root domain as suggested
 * in the paper Optimal Additive Composition of Abstraction-based Admissible Heuristics.
 */


class LPBinaryForks_KD: public LPBinaryFork {
	virtual LPConstraint* set_h_constraint(int sigma) const;

public:
	LPBinaryForks_KD();
	LPBinaryForks_KD(GeneralAbstraction* abs);
	virtual ~LPBinaryForks_KD();

	virtual void set_static_constraints();
	virtual void get_dynamic_constraints(const State* state, vector<LPConstraint*>& dyn_constr);

};

#endif /* LP_BINARY_FORKS_KD_H_ */
