#include "LPConstraint.h"
#include <math.h>
#include <cfloat>
#include <cassert>


LPConstraint::LPConstraint() {
	lb = 0.0;
	ub = DBL_MAX;
	to_keep = true;
	index = 0;
}

LPConstraint::LPConstraint(LPConstraint* lpc, bool keep) {
	lb = lpc->get_lb();
	ub = lpc->get_ub();
	to_keep = keep;
	index = lpc->get_index();
	vars = lpc->get_vals();
	c_vars = lpc->get_c_vars();
}


LPConstraint::LPConstraint(double l, double u, bool keep): lb(l), ub(u), to_keep(keep) {
	index = 0;
}

LPConstraint::~LPConstraint() {
	delete_constr();
}

void LPConstraint::add_val(int var, double val) {
	assert(var>=0);
	if (c_vars.find(var) == c_vars.end()) {
		c_vars[var] = val;
	} else {
		c_vars[var] += val;
	}
}

void LPConstraint::finalize() {

	for( map<int,double>::iterator ii=c_vars.begin(); ii!=c_vars.end(); ++ii) {
	   vars.push_back(new ConstraintVar((*ii).first, (*ii).second));
	}
	c_vars.clear();
}

const vector<ConstraintVar*>& LPConstraint::get_vals() const {
	return vars;
}

const map<int, double>& LPConstraint::get_c_vars() const {
	return c_vars;
}


void LPConstraint::free_mem() {
	if (!to_keep) {
		delete_constr();
	}
}


void LPConstraint::delete_constr() {
	for (int i = 0; i < vars.size(); i++) {
		if (vars[i]) {
			delete vars[i];
		}
	}
	vars.clear();
}


void LPConstraint::dump() {
	if (0 == vars.size())
		return;
	cout << "  " << lb << " <= ";
	vars[0]->dump(index);
//    	cout << vars[0]->get_val << " * x_" << vars[0]->get_var;
	for (int i = 1; i < vars.size(); i++) {
		cout << " + ";
		vars[i]->dump(index);
	}
	cout << " <= " << ub << endl;
}
