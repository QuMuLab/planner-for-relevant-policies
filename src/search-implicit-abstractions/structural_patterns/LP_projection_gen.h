#ifndef LP_PROJECTION_GEN_H_
#define LP_PROJECTION_GEN_H_

#include "var_projection.h"
#include "projection_gen.h"
#include <cfloat>

class LPProjection: public Projection {

public:
	LPProjection();
	LPProjection(GeneralAbstraction* abs);
	LPProjection(vector<int>& pattern);
	virtual ~LPProjection();

	virtual void initiate();
	virtual void set_static_constraints();
//	virtual void solve();
	virtual void get_dynamic_constraints(const State* state, vector<LPConstraint*>& dyn_constr);

	virtual void add_distance_constraints(vector<int> free_vars, vector<int> state, const vector<int>& doms, Operator* op);
	virtual void add_goal_constraints(vector<int> free_vars, vector<int> state, const vector<int>& doms);

	virtual void remove_abstract_operators() {}

	virtual int h_var() const;
	virtual int w_var(Operator* a) const;
//	virtual int num_w_var_vars() const;

};

#endif /* LP_PROJECTION_GEN_H_ */
