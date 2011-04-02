#ifndef LP_PROJECTION_OFF_H_
#define LP_PROJECTION_OFF_H_

#include "var_projection.h"
#include "LP_projection_gen.h"
#include <cfloat>

class LPProjection_OFF: public LPProjection {

public:
	LPProjection_OFF();
	LPProjection_OFF(GeneralAbstraction* abs);
	LPProjection_OFF(vector<int>& pattern);
	virtual ~LPProjection_OFF();

//	void initiate();

	virtual void set_objective();
//	virtual void set_static_constraints();
	virtual void get_dynamic_constraints(const State*, vector<LPConstraint*>& ) {exit(1);}
//	virtual void solve() {}

	virtual void add_distance_constraints(vector<int> free_vars, vector<int> state, const vector<int>& doms, Operator* op);
	virtual void add_goal_constraints(vector<int> free_vars, vector<int> state, const vector<int>& doms);


};

#endif /* LP_PROJECTION_OFF_H_ */
