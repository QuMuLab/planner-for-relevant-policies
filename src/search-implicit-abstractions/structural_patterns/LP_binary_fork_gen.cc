#include "LP_binary_fork_gen.h"
#include "mapping.h"
#include <math.h>
#include "binary_forks_gen.h"


LPBinaryFork::LPBinaryFork() :BinaryFork() {
}

LPBinaryFork::LPBinaryFork(GeneralAbstraction* abs) :BinaryFork(abs) {
}

LPBinaryFork::LPBinaryFork(ForksAbstraction* f, Domain* abs_domain) :BinaryFork(f, abs_domain) {
}

LPBinaryFork::~LPBinaryFork() {

	free_constraints();
}

void LPBinaryFork::free_constraints() {
	SolutionMethod::free_constraints();

	for (int i=0; i < dynamic_LPConstraints[0].size();i++) {
		delete dynamic_LPConstraints[0][i];
	}
	dynamic_LPConstraints[0].clear();

	for (int i=0; i < dynamic_LPConstraints[1].size();i++) {
		delete dynamic_LPConstraints[1][i];
	}
	dynamic_LPConstraints[1].clear();
}


void LPBinaryFork::initiate() {
	BinaryFork::initiate();
	// Updating the number of w_var variables
	number_of_w_var_variables = get_mapping()->get_abstract()->get_actions_number();
}

/*
void LPBinaryFork::initiate() {
	BinaryFork::initiate();
	BinaryFork::solve();

	const Problem* abs = get_mapping()->get_abstract();
	const vector<int> &doms = abs->get_variable_domains();

	// Updating the lower and upper bounds on sigma per value
	int root_goal = abs->get_goal_val(0);
	for (int v = 1; v < doms.size(); v++) {
		for (int val = 0; val < doms[v]; val++) {
			for (int theta = 0; theta < doms[0]; theta++) {
				int u = get_sigma_upper_bound(v,val,theta);
				int d_ind = d_var(v,val,u,theta);
				int upper_b = solution->get_value(d_ind) + 1;

				if (-1 != root_goal){ // There is a goal on the root
					if (theta == root_goal) { //  if the goal is defined and equal to the initial,
						if ((upper_b % 2) == 0)
							upper_b++;
					} else {
						if ((upper_b % 2) == 1)
							upper_b++;
					}
				}

				set_sigma_upper_bound(v,val,theta,upper_b);
			}
		}
	}

}
*/
void LPBinaryFork::set_static_constraints() {

	const Problem* abs = get_mapping()->get_abstract();
	const vector<int> &doms = abs->get_variable_domains();

	//For each leaf v (the first variable is always the root)
	int var_num = doms.size();
	for (int v = 1; v < var_num; v++) {
		int dom_size = doms[v];
		int g_v = abs->get_goal_val(v);
		const vector<Operator*> &A_v = abs->get_var_actions(v);

		int A_v_size = A_v.size();

		// For each value val_0 in Domain(v)
		for (int val_0=0; val_0 < dom_size; val_0++){
			for (int theta=0; theta < doms[0]; theta++){

				// (III) - Static
				// p(v, val_0, val_0, theta) = 0
				int p_ind = p_var(v,val_0,val_0,theta);
				static_LPConstraints.push_back(set_x_eq_0_constraint(p_ind, true));

				// (II).1 - Dynamic
				// d(v, val_0, 1, theta) = p(v, val_0, G[v], theta)
				if (1 == get_sigma_lower_bound(v,val_0,theta)) {
					int d_ind0 = d_var(v,val_0,1,theta);
					int p_ind0 = p_var(v,val_0,g_v,theta);
					static_LPConstraints.push_back(set_x_eq_y_constraint(d_ind0,p_ind0, true));
				}
				// (II).2 - Dynamic
				// For each value val_1 in Domain(v)
				for (int val_1=0; val_1 < dom_size; val_1++){
					// For each 1 < sz <= |\sigma(r)|
					int first_support = max(get_sigma_lower_bound(v, val_1,theta),2);
					int last_support = get_sigma_upper_bound(v, val_1,theta);
					for (int sz=first_support; sz <= last_support; sz++){
						// d(v, val_1, sz, theta) <= d(v, val_0, sz-1, 1-theta) + p(v, val_1, val_0, theta)

						if (get_sigma_lower_bound(v,val_0,1-theta) >= sz)
							continue;
						int d_ind0 = d_var(v,val_1,sz,theta);
						int upper_b = min(get_sigma_upper_bound(v,val_0,1-theta),sz-1);
						assert(upper_b > 0);
						int d_ind1 = d_var(v,val_0,upper_b,1-theta);
//						int d_ind1 = d_var(v,val_0,sz-1,1-theta);
						int p_ind = p_var(v,val_1,val_0,theta);

						static_LPConstraints.push_back(set_x_leq_y_plus_z_constraint(d_ind0,d_ind1, p_ind, true));
					}
				}
			}
			// (III) - Static cont.
			for (int a = 0; a < A_v_size; a++) {
				int prv = A_v[a]->get_prevail_val(0);
				int pre = A_v[a]->get_pre_val(v);
				int post = A_v[a]->get_post_val(v);
				int w_ind0 = w_var(A_v[a]);
				int prv_b = (-1 == prv) ? 0 : prv;
				int prv_e = (-1 == prv) ? doms[0]-1 : prv;

				for (int theta=prv_b; theta <= prv_e; theta++){
					// p(v, val_0, post(a)[v], 0/1) <= p(v, val_0, pre(a)[v], 0/1) + w(a)
					int p_ind0 = p_var(v,val_0,post,theta);

					if (-1 == pre) {
						static_LPConstraints.push_back(set_x_leq_y_constraint(p_ind0,w_ind0,true));
					} else {
						int p_ind1 = p_var(v,val_0,pre,theta);
						static_LPConstraints.push_back(set_x_leq_y_plus_z_constraint(p_ind0,p_ind1,w_ind0,true));
					}
				}
			}
		}
	}

	const vector<Operator*> &A_r = abs->get_var_actions(0);

	// Dividing root changing actions into two sets, by the post value
	int w_ind0 = w_r(0);
	int w_ind1 = w_r(1);
	for (int a = 0; a < A_r.size(); a++) {
		// If the action does nothing...
		if (A_r[a]->get_pre_val(0) == A_r[a]->get_post_val(0))
			continue;

		if (0 != A_r[a]->get_post_val(0)) {
			int w_ind2 = w_var(A_r[a]);
			dynamic_LPConstraints[0].push_back(set_x_leq_y_constraint(w_ind0,w_ind2,true));
			dynamic_LPConstraints[1].push_back(set_x_leq_y_constraint(w_ind1,w_ind2,true));
		} else {
			int w_ind3 = w_var(A_r[a]);
			dynamic_LPConstraints[0].push_back(set_x_leq_y_constraint(w_ind1,w_ind3,true));
			dynamic_LPConstraints[1].push_back(set_x_leq_y_constraint(w_ind0,w_ind3,true));
		}
	}
}

void LPBinaryFork::get_dynamic_constraints(const State* state, vector<LPConstraint*> &dyn_constr) {

	Mapping* map = get_mapping();
	const Problem* abs = map->get_abstract();
	const State* abs_state = map->get_abs_state(state);
	const state_var_t * eval_state = abs_state->get_buffer();

	int root_zero = (int) eval_state[0];
	int root_goal = abs->get_goal_val(0);

	dyn_constr = dynamic_LPConstraints[root_zero];

	// Here we add the rest of the dynamic constraints
	// Counting the lower and upper bounds on sigma
	int lower_b = 0;
	int upper_b = 0;
	for (int v = 1; v <= num_leafs; v++) {
		int val = (int) eval_state[v];
		int lower_v = get_sigma_lower_bound(v,val,root_zero);
		int upper_v = get_sigma_upper_bound(v,val,root_zero);
//		if (STATISTICS >= 2) {
//			cout << " " << upper_v;
//		}

		lower_b = (lower_b < lower_v) ? lower_v : lower_b;
		upper_b = (upper_b < upper_v) ? upper_v : upper_b;
	}
//	if (STATISTICS >= 2) {
//		cout << endl;
//	}

	int step = 1;	      // The step of the sigma
	if (-1 != root_goal){ // There is a goal on the root -- go over all even/odd possibilities for sigma
		step = 2;                      	// the step is 2
		if (root_zero == root_goal) {   //  if the goal is defined and equal to the initial,
			if ((lower_b % 2) == 0)
				lower_b++;              //   then sigma's length is odd (1, 3, 5, etc).
			if ((upper_b % 2) == 0)
				upper_b++;
		} else {
			if ((lower_b % 2) == 1)
				lower_b++;              // otherwise, sigma's length is even (2, 4, 6, etc).
			if ((upper_b % 2) == 1)
				upper_b++;
		}
	}
//	if (STATISTICS >= 2) {
//		if ((lower_b > step) || (upper_b < sigma_size))
//			cout << "Lower bound: " << lower_b <<", Upper bound: " << upper_b << " ("<< sigma_size<<"), step: " << step << endl;
//	}
	for (int sigma = lower_b; sigma<=upper_b; sigma=sigma+step ) {
		// (I) Dynamic
		// h <= cost of root changing actions + sum of d(v,G[v],|sigma|)
		dyn_constr.push_back(set_h_constraint(sigma,eval_state));
	}

}


LPConstraint* LPBinaryFork::set_h_constraint(int sigma, const state_var_t * eval_state) const {

	int root_zero = (int) eval_state[0];
	// (I) Dynamic
	// h <= cost of root changing actions + sum of d(v,s[v],|sigma|,s[r])

	LPConstraint* lpc = new LPConstraint(0.0,DBL_MAX,false);

	int h_ind = h_var();
	lpc->add_val(h_ind, -1.0);

	//For each leaf v (the first variable is always the root)
	for (int v = 1; v <= num_leafs; v++) {
		int val = (int) eval_state[v];
		int fixed = min(get_sigma_upper_bound(v,val,root_zero),sigma);
		assert(fixed > 0);
//		int d_ind = d_var(v,val,sigma,root_zero);
		int d_ind = d_var(v,val,fixed,root_zero);
		lpc->add_val(d_ind, 1.0);
	}

	if (sigma == 1) {
		lpc->finalize();
		return lpc;
	}

	double sig =  ((double) sigma - 1)/2;
	int w_coeff0 = ceil(sig);
	int w_ind0 = w_r(0);

	lpc->add_val(w_ind0, w_coeff0);
	if (sigma > 2) {
		int w_ind1 = w_r(1);
		int w_coeff1 = floor(sig);
		lpc->add_val(w_ind1, w_coeff1);
	}

	lpc->finalize();
	return lpc;
}

// Change the constraints and the indexes


int LPBinaryFork::w_var(Operator* a) const {
	const Problem* abs = get_mapping()->get_abstract();
	int ret = number_of_d_variables + number_of_p_variables + number_of_h_variables +
	   number_of_w_r_variables + number_of_w_v_variables + abs->get_action_index(a);
//	cout << "x_" << ret << " = w_a, a:";
//	a->dump();
	return ret;
}
