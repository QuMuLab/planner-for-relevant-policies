#ifndef LP_BINARY_FORKS_OFF_H_
#define LP_BINARY_FORKS_OFF_H_

#include "LP_abstraction.h"
#include "binary_forks.h"
#include <cfloat>
#include "solution.h"

/* This class describes LP construction for forks with binary root domain as suggested
 * in the paper Optimal Additive Composition of Abstraction-based Admissible Heuristics.
 */

class LPBinaryForks_OFF: public LPAbstraction {
	int sigma_size;
	int num_leafs;

public:
	LPBinaryForks_OFF();
	LPBinaryForks_OFF(GeneralAbstraction* abs);
	virtual ~LPBinaryForks_OFF();

	void initiate();
	virtual void set_objective() {
		cout << "Function set_objective() not implemented for LPBinaryForks_OFF class" << endl;
		exit(1);
	}
	virtual void set_static_constraints() {
		cout << "Function set_static_constraints() not implemented for LPBinaryForks_OFF class" << endl;
		exit(1);
	}
	virtual void get_dynamic_constraints(const State*, vector<LPConstraint*>& ) {
		cout << "Function get_dynamic_constraints() not implemented for LPBinaryForks_OFF class" << endl;
		exit(1);
	}
	virtual void solve();

	double get_h_val(int sigma, const state_var_t * eval_state) const;
	virtual double get_solution_value(const State* state);
	int d_var(int var, int val, int i, int theta) const;
	int p_var(int var, int val1, int val2, int root_val) const;

	virtual int h_var() const;
	virtual int w_r(int root_zero) const;
	virtual int w_var(Operator* a) const;
	virtual int get_num_vars() const;

	virtual void dump() const;

};

#endif /* LP_BINARY_FORKS_OFF_H_ */
