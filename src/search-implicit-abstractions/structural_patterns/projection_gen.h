#ifndef PROJECTION_GEN_H_
#define PROJECTION_GEN_H_

#include "var_projection.h"
#include <cfloat>
#include "solution_method.h"

class Projection: public SolutionMethod {
	int num_vars;
//	int num_states;
	vector<int> multiplier;

protected:
	void set_distances(double **sol, vector<int> free_vars, vector<int> state, const vector<int>& doms, Operator* op);
	void set_goal_distances(double **sol, vector<int> free_vars, vector<int> state, const vector<int>& doms, int last);

	int number_of_d_variables, number_of_h_variables, number_of_w_var_variables;
public:
	Projection();
	Projection(GeneralAbstraction* abs);
	Projection(vector<int>& pattern);
	virtual ~Projection();

	virtual void initiate();
	virtual void solve();
	virtual double get_solution_value(const State* state);

	int d_var(const State* state) const;
	int d_var(vector<int>& state) const;
//	virtual int num_d_vars() const {return num_states;}
//	virtual int num_h_vars() const {return 1;}
//	virtual int num_w_var_vars() const {return 0;}

	virtual int get_num_vars() const;

};

#endif /* PROJECTION_GEN_H_ */
