#ifndef LP_SOLVER_H_
#define LP_SOLVER_H_

#include "LPConstraint.h"
#include "solution.h"

class LP_solver {
public:
	LP_solver();
	virtual ~LP_solver();

	virtual void initialize() = 0;
	virtual void free_mem() = 0;

	virtual void set_size(int n_cols, int n_rows, int n_nonzeros) = 0;

	virtual double solve(vector<ConstraintVar*>& obj_func, vector<LPConstraint*>& constr, Solution* sol) = 0;
};

#endif /* LP_SOLVER_H_ */
