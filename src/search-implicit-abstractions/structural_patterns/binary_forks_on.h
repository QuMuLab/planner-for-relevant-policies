#ifndef BINARY_FORKS_ON_H_
#define BINARY_FORKS_ON_H_

#include "binary_forks.h"
#include <cfloat>
#include "solution.h"
#include "binary_forks_gen.h"

/* This class describes LP construction for forks with binary root domain as suggested
 * in the paper Optimal Additive Composition of Abstraction-based Admissible Heuristics.
 */


class BinaryForks_ON: public BinaryFork {

public:
	BinaryForks_ON();
	BinaryForks_ON(GeneralAbstraction* abs);
	BinaryForks_ON(ForksAbstraction* f, Domain* abs_domain);
	virtual ~BinaryForks_ON();

//	virtual int num_d_vars() const {return num_leafs*sigma_size*sigma_size;}

	virtual double get_solution_value(const State* state);
	virtual double get_h_val(int sigma, const state_var_t * eval_state) const;
//	virtual int d_var(int var, int val, int i, int theta = 0) const;

	virtual void solve() {}
	virtual void remove_abstract_operators() {}

};

#endif /* BINARY_FORKS_ON_H_ */
