#ifndef SOLUTION_METHOD_H_
#define SOLUTION_METHOD_H_

#include "general_abstraction.h"
#include "solution.h"
#include "mapping.h"
#include "../problem.h"
#include "LPConstraint.h"

class SolutionMethod {

protected:
	int index;
	Solution* solution;
	GeneralAbstraction* abstraction;
	bool active;

	// Moved from LPAbstraction
	LPConstraint* obj_func;
	vector<LPConstraint*> static_LPConstraints;

	int d_vars_multiplier; // For moving from LP to offline

public:
	SolutionMethod(int d_vars_mult = 2);
	virtual ~SolutionMethod();

	Mapping* get_mapping() const;
	void set_mapping(Mapping* map);

	int get_abstraction_type() const;
	void set_abstraction_type(int type);

	void set_root_var_and_domain(Domain* new_dom) {abstraction->set_root_var_and_domain(new_dom);}
	void set_pattern(vector<int>& pattern) {abstraction->set_pattern(pattern);}
	void create(const Problem* p) {abstraction->create(p);}

	int get_abstraction_index() const {return index;}
	void set_abstraction_index(int ind) {index = ind;}

	virtual double get_solution_value(const State* state) = 0;
	virtual void set_solution(Solution* sol);
	virtual Solution* get_solution();

	GeneralAbstraction* get_abstraction() const;

	void set_abstraction(GeneralAbstraction* abs);
	bool is_active() const;
	void activate();
	void deactivate();
	virtual void remove_abstract_operators() {abstraction->remove_abstract_operators();}

	// Moved from Abstractions
	virtual void initiate() = 0;
	virtual void solve() = 0;
	virtual int get_num_vars() const = 0;


	// Moved from LPAbstraction
	virtual void set_objective();
	virtual void set_static_constraints() {exit(1);}

	void get_objective(vector<ConstraintVar*>& res) const;
	void get_static_constraints(vector<LPConstraint*> &stat_constr) const;
	virtual void get_dynamic_constraints(const State*, vector<LPConstraint*> &) {exit(1);}
	int append_constraints(const State* state, vector<LPConstraint*> &constr);

	LPConstraint* set_x_eq_0_constraint(int x, bool tokeep) const;
	LPConstraint* set_x_eq_y_constraint(int x, int y, bool tokeep) const;
	LPConstraint* set_x_leq_y_constraint(int x, int y, bool tokeep) const;
	LPConstraint* set_x_leq_y_plus_z_constraint(int x, int y, int z, bool tokeep) const;

	virtual void dump() const;
	virtual int h_var() const {exit(1);}
	virtual int w_var(Operator* ) const {exit(1);}

	void set_d_vars_multiplier(int val) {d_vars_multiplier = val;}
	virtual void set_default_number_of_variables() {}

	virtual void free_constraints();

};

#endif /* SOLUTION_METHOD_H_ */
