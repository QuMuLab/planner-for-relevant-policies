#ifndef PROJECTION_ON_H_
#define PROJECTION_ON_H_

#include "projection_gen.h"
//#include "var_projection.h"
#include "general_abstraction.h"
//#include <cfloat>

class Projection_ON: public Projection {
public:
	Projection_ON();
	Projection_ON(GeneralAbstraction* abs);
	Projection_ON(vector<int>& pattern);
	virtual ~Projection_ON();

	virtual double get_solution_value(const State* state) {
		solve();
		return Projection::get_solution_value(state);
	}
	virtual void remove_abstract_operators() {}

};

#endif /* PROJECTION_ON_H_ */
