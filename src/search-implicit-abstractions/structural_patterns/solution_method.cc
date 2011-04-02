#include "solution_method.h"
#include <cfloat>

SolutionMethod::SolutionMethod(int d_vars_mult) :d_vars_multiplier(d_vars_mult) {
	index = 0;
	active = true;
//	active = false;
	solution = NULL;
	abstraction = NULL;
	// Moved from LPAbstraction
	obj_func = NULL;

}

SolutionMethod::~SolutionMethod() {
	if (solution)
		delete solution;
	if (abstraction)
		delete abstraction;

	// Moved from LPAbstraction
	SolutionMethod::free_constraints();
/*
	if (obj_func)
		delete obj_func;
*/

}

void SolutionMethod::free_constraints() {
	int sz = static_LPConstraints.size();
	for (int i=0;i<sz;i++){
		delete static_LPConstraints[i];
    }
	static_LPConstraints.clear();
}


Mapping* SolutionMethod::get_mapping() const {
	return abstraction->get_mapping();
}

void SolutionMethod::set_mapping(Mapping* map) {
	abstraction->set_mapping(map);
}


int SolutionMethod::get_abstraction_type() const {
	return abstraction->get_abstraction_type();
}

void SolutionMethod::set_abstraction_type(int type) {
	abstraction->set_abstraction_type(type);
}




void SolutionMethod::set_solution(Solution* sol){
	if (solution)
		delete solution;
	solution = sol;
}

Solution* SolutionMethod::get_solution(){
	return solution;
}

GeneralAbstraction* SolutionMethod::get_abstraction() const {
	return abstraction;
}

void SolutionMethod::set_abstraction(GeneralAbstraction* abs) {
	abstraction = abs;
}

bool SolutionMethod::is_active() const {
	return active;
}

void SolutionMethod::activate() {
	active = true;
}

void SolutionMethod::deactivate() {
	active = false;
}

// Moved from LPAbstraction
void SolutionMethod::set_objective() {
	obj_func = new LPConstraint();
	int h = h_var();
	obj_func->add_val(h, 1.0);
	obj_func->finalize();
}

void SolutionMethod::get_objective(vector<ConstraintVar*>& res) const {
	res = obj_func->get_vals();
}

void SolutionMethod::get_static_constraints(vector<LPConstraint*> &stat_constr) const {
	stat_constr = static_LPConstraints;
}


int SolutionMethod::append_constraints(const State* state, vector<LPConstraint*> &constr) {

	int res = 0;
	vector<LPConstraint*> static_constr;
	get_static_constraints(static_constr);
	int static_size = static_constr.size();
	for (int i = 0; i < static_size; i++) {
		static_constr[i]->set_index(get_abstraction_index());
		constr.push_back(static_constr[i]);
		res+=static_constr[i]->get_num_vars();
//		if (STATISTICS >= 2) {
//			cout << index << ":  ";
//			static_constr[i]->dump();
//		}
	}

	vector<LPConstraint*> dyn_constr;
	get_dynamic_constraints(state, dyn_constr);
	int dyn_size = dyn_constr.size();
	for (int i = 0; i < dyn_size; i++) {
		dyn_constr[i]->set_index(get_abstraction_index());
		constr.push_back(dyn_constr[i]);
		res += dyn_constr[i]->get_num_vars();
//		if (STATISTICS >= 2) {
//			cout << index << ":  ";
//			dyn_constr[i]->dump();
//		}
	}
	return res;
}



LPConstraint* SolutionMethod::set_x_eq_0_constraint(int x, bool tokeep) const {
	// x = 0
	LPConstraint* lpc = new LPConstraint(0.0,0.0,tokeep);
	lpc->add_val(x, 1.0);
	lpc->finalize();
	return lpc;
}

LPConstraint* SolutionMethod::set_x_eq_y_constraint(int x, int y, bool tokeep) const {
	// x = y
	LPConstraint* lpc = new LPConstraint(0.0,0.0,tokeep);

	lpc->add_val(x, -1.0);
	lpc->add_val(y, 1.0);
	lpc->finalize();
	return lpc;
}

LPConstraint* SolutionMethod::set_x_leq_y_constraint(int x, int y, bool tokeep) const {
	// x <= y
	LPConstraint* lpc = new LPConstraint(0.0,DBL_MAX,tokeep);

	lpc->add_val(x, -1.0);
	lpc->add_val(y, 1.0);

	lpc->finalize();
	return lpc;
}

LPConstraint* SolutionMethod::set_x_leq_y_plus_z_constraint(int x, int y, int z, bool tokeep) const {
	// x <= y + z
	LPConstraint* lpc = new LPConstraint(0.0,DBL_MAX,tokeep);

	lpc->add_val(x, -1.0);
	lpc->add_val(y, 1.0);
	lpc->add_val(z, 1.0);

	lpc->finalize();
	return lpc;
}


void SolutionMethod::dump() const {

	cout << "Objective function:" << endl;
	cout << "max " ;
	for (int i = 0; i < obj_func->get_vals().size(); i++)
		cout << " + " << obj_func->get_vals()[i]->val << " * x_" << obj_func->get_vals()[i]->var;
	cout << endl;

	cout << "Static Constraints:" << endl;
	vector<LPConstraint*> static_constr;
	get_static_constraints(static_constr);
	for (int i = 0; i < static_constr.size(); i++)
		static_constr[i]->dump();
/*
	cout << "Dynamic constraints for state " << endl;
	state->dump();
	vector<LPConstraint*> dyn_constr;
	get_dynamic_constraints(state, dyn_constr);

	for (int i = 0; i < dyn_constr.size(); i++)
		dyn_constr[i]->dump();
*/
}




