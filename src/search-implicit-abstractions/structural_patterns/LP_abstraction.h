#ifndef LP_ABSTRACTION_H_
#define LP_ABSTRACTION_H_

#include "general_abstraction.h"
#include "LPConstraint.h"

class LPAbstraction {

protected:
	LPConstraint* obj_func;
	vector<LPConstraint*> static_LPConstraints;

public:
	LPAbstraction();
	virtual ~LPAbstraction();

	virtual void set_objective();
	virtual void set_static_constraints() = 0;

	void get_objective(vector<ConstraintVar*>& res) const;
	void get_static_constraints(vector<LPConstraint*> &stat_constr) const;
	virtual void get_dynamic_constraints(const State* state, vector<LPConstraint*> &dyn_constr) const = 0;
	virtual int append_constraints(const State* state, vector<LPConstraint*> &constr) const;

	LPConstraint* set_x_eq_0_constraint(int x, bool tokeep) const;
	LPConstraint* set_x_eq_y_constraint(int x, int y, bool tokeep) const;
	LPConstraint* set_x_leq_y_constraint(int x, int y, bool tokeep) const;
	LPConstraint* set_x_leq_y_plus_z_constraint(int x, int y, int z, bool tokeep) const;

	virtual void dump() const;
	virtual int h_var() const = 0;
	virtual int w_var(Operator* a) const = 0;
	virtual int get_abstraction_index() const = 0;
};

#endif /* LP_ABSTRACTION_H_ */
