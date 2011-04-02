#include "SP_globals.h"
#include "binary_forks_on.h"
#include "mapping.h"
#include <math.h>
#include "binary_forks_gen.h"


BinaryForks_ON::BinaryForks_ON() :BinaryFork() {
	set_d_vars_multiplier(1);
}

BinaryForks_ON::BinaryForks_ON(GeneralAbstraction* abs) :BinaryFork(abs){
	set_d_vars_multiplier(1);
}

BinaryForks_ON::BinaryForks_ON(ForksAbstraction* f, Domain* abs_domain) :BinaryFork(f,abs_domain) {
	set_d_vars_multiplier(1);
}

BinaryForks_ON::~BinaryForks_ON() {
}

double BinaryForks_ON::get_solution_value(const State* state) {
	// Solving the problem, and keeping the solution
	BinaryFork::solve(state);
	double ret = BinaryFork::get_solution_value(state);
//	cout << ret << endl;
	return ret;
}


double BinaryForks_ON::get_h_val(int sigma, const state_var_t * eval_state) const {

	int root_zero = (int) eval_state[0];
	//For each leaf v (the first variable is always the root)
	double sol = 0.0;
	double sig =  ((double) sigma - 1)/2;
	if (sigma > 1) {
		int w_ind0 = w_r(1 - root_zero);
		double s = solution->get_value(w_ind0);
		if (s >= LP_INFINITY)
			return s;
		int w_coeff0 = ceil(sig);
		sol += (w_coeff0 * s);
	}
	if (sigma > 2) {
		int w_ind1 = w_r(root_zero);
		double s = solution->get_value(w_ind1);
		if (s >= LP_INFINITY)
			return s;
		int w_coeff1 = floor(sig);
		sol += (w_coeff1 * s);
	}
	const Problem* abs = get_mapping()->get_abstract();
	for (int v = 1; v <= num_leafs; v++) {
		int g_v = abs->get_goal_val(v);
		int upper_b = get_sigma_upper_bound(v,g_v,root_zero);
		int v_sigma = (sigma < upper_b) ? sigma : upper_b;  // min(sigma, upper_b);
		int d_ind = d_var(v,g_v,v_sigma,root_zero);
		double s =solution->get_value(d_ind);
		if (s >= LP_INFINITY)
			return s;
		sol += s;
	}
	return sol;
}
/*
int BinaryForks_ON::d_var(int var, int val, int i, int ) const {
	return BinaryFork::d_var(var,val,i);
}
*/
