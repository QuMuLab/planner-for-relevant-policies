#include "LP_abstraction.h"
#include <cfloat>

LPAbstraction::LPAbstraction() {
	cout << "LPAbstraction::LPAbstraction()" << endl;
	obj_func = NULL;
}

LPAbstraction::~LPAbstraction() {
	int sz = static_LPConstraints.size();
	for (int i=0;i<sz;i++){
		delete static_LPConstraints[i];
    }
/*
	if (obj_func)
		delete obj_func;
*/
}


void LPAbstraction::set_objective() {
	cout << "LPAbstraction::set_objective()" << endl;

	obj_func = new LPConstraint();
	int h = h_var();
	obj_func->add_val(h, 1.0);
	obj_func->finalize();
	cout << "Objective is set " << obj_func << endl;
}

void LPAbstraction::get_objective(vector<ConstraintVar*>& res) const {

	cout << "Getting objective " << obj_func << endl;
	res = obj_func->get_vals();
	cout << "Done getting objective" << endl;
}

void LPAbstraction::get_static_constraints(vector<LPConstraint*> &stat_constr) const {
	stat_constr = static_LPConstraints;
}


int LPAbstraction::append_constraints(const State* state, vector<LPConstraint*> &constr) const {

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



LPConstraint* LPAbstraction::set_x_eq_0_constraint(int x, bool tokeep) const {
	// x = 0
	LPConstraint* lpc = new LPConstraint(0.0,0.0,tokeep);
	lpc->add_val(x, 1.0);
	lpc->finalize();
	return lpc;
}

LPConstraint* LPAbstraction::set_x_eq_y_constraint(int x, int y, bool tokeep) const {
	// x = y
	LPConstraint* lpc = new LPConstraint(0.0,0.0,tokeep);

	lpc->add_val(x, -1.0);
	lpc->add_val(y, 1.0);
	lpc->finalize();
	return lpc;
}

LPConstraint* LPAbstraction::set_x_leq_y_constraint(int x, int y, bool tokeep) const {
	// x <= y
	LPConstraint* lpc = new LPConstraint(0.0,DBL_MAX,tokeep);

	lpc->add_val(x, -1.0);
	lpc->add_val(y, 1.0);

	lpc->finalize();
	return lpc;
}

LPConstraint* LPAbstraction::set_x_leq_y_plus_z_constraint(int x, int y, int z, bool tokeep) const {
	// x <= y + z
	LPConstraint* lpc = new LPConstraint(0.0,DBL_MAX,tokeep);

	lpc->add_val(x, -1.0);
	lpc->add_val(y, 1.0);
	lpc->add_val(z, 1.0);

	lpc->finalize();
	return lpc;
}


void LPAbstraction::dump() const {

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


