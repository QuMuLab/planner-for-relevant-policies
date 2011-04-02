#include "LP_binary_forks_bounds.h"
#include "mapping.h"
#include <math.h>
#include <cassert>


LPBinaryForks_b::LPBinaryForks_b() :LPBinaryFork() {
	set_d_vars_multiplier(1);
}

LPBinaryForks_b::LPBinaryForks_b(GeneralAbstraction* abs) :LPBinaryFork(abs) {
	set_d_vars_multiplier(1);
}
LPBinaryForks_b::LPBinaryForks_b(ForksAbstraction* f, Domain* abs_domain) :LPBinaryFork(f, abs_domain) {
	set_d_vars_multiplier(1);
}


LPBinaryForks_b::~LPBinaryForks_b() {
}

void LPBinaryForks_b::initiate() {
	LPBinaryFork::initiate();
	number_of_w_v_variables = 2*num_leafs*sigma_size*sigma_size;
/*
	cout << number_of_d_variables << " " << number_of_h_variables <<
	" " << number_of_p_variables <<
	" " << number_of_w_r_variables <<
	" " << number_of_w_v_variables <<
	" " << number_of_w_var_variables << endl;
*/
}

void LPBinaryForks_b::set_bounds_for_state(const State* state) {

	BinaryFork::solve(state);

	Mapping* map = get_mapping();
	const Problem* abs = map->get_abstract();

	const vector<int> &doms = abs->get_variable_domains();

	const State* abs_state = map->get_abs_state(state);
	const state_var_t * eval_state = abs_state->get_buffer();

	int root_zero = (int) eval_state[0];
	int root_goal = abs->get_goal_val(0);

	for (int v = 1; v < doms.size(); v++) {
		for (int val = 0; val < doms[v]; val++) {
			int upper_b = get_domain_bound(v, val, eval_state);

//			int b_ind = bound_ind(v,val,root_zero);
			if (-1 != root_goal){ // There is a goal on the root
				if (root_zero == root_goal) {  //  if the goal is defined and equal to the initial,
					if ((upper_b % 2) == 0)
						upper_b++;
				} else {
					if ((upper_b % 2) == 1)
						upper_b++;
				}
			}
			set_sigma_upper_bound(v,val,root_zero,upper_b);
		}
	}
}


//TODO: rewrite this function to precalculate these values.
// WARNING: Check correctness!!!
int LPBinaryForks_b::get_domain_bound(int v, int g_v, const state_var_t * eval_state) const {
	Mapping* map = get_mapping();
	const Problem* abs = map->get_abstract();

	const vector<Operator*> &ops = abs->get_var_actions(v);


	int root_dom = abs->get_variable_domain(0);  // Should be 2
	int dom = abs->get_variable_domain(v);
	bool **in_arcs = new bool*[dom];
	bool **out_arcs = new bool*[dom];
	bool *in_uncond = new bool[dom];

	for (int val = 0; val < dom; val++){
		in_arcs[val] = new bool[root_dom];
		out_arcs[val] = new bool[root_dom];
		for (int theta = 0; theta < root_dom; theta++){
			in_arcs[val][theta] = false;
			out_arcs[val][theta] = false;
		}
		in_uncond[val] = false;
	}

	for (int a = 0; a < ops.size(); a++) {
		int pre = ops[a]->get_pre_val(v);
		int post = ops[a]->get_post_val(v);
		int prv = ops[a]->get_prevail_val(0);

		int pre_b = (-1 == pre) ? 0 : pre;       // Precondition range
		int pre_e = (-1 == pre) ? dom-1 : pre;

		if (-1 == prv ) { // only in arcs are kept
			in_uncond[post] = true;         // in arc
		} else {
			in_arcs[post][prv] = true;         // in arc

			for (int val = pre_b; val <= pre_e; val++){
				out_arcs[val][prv] = true;    // out arc
			}
		}
	}

	int s_v = (int) eval_state[v];
	int root_zero = (int) eval_state[0];

	int ret = 1;  // we start with one, counting the size of the support, and not the number
	// of value changes.
	// if you can go in under one root value, and out under another, the value is counted.
	// for initial value, if you can go out with non-root-zero, then count
	for (int val = 0; val < dom; val++){
		if (val == s_v) {
			if (out_arcs[val][1-root_zero]) {
				ret++;
			}
		} else if (val != g_v) { // nothing to count for goal value
			if ((in_arcs[val][0] && out_arcs[val][1]) ||
				(in_arcs[val][1] && out_arcs[val][0]) ||
				(in_uncond[val] && ( out_arcs[val][0] || out_arcs[val][1]))) {
				ret++;
			}
		}
	}
	// Deallocating memory for arcs arrays
	for (int val = 0; val < dom; val++){
		delete [] in_arcs[val];
		delete [] out_arcs[val];
	}
	delete [] in_arcs;
	delete [] out_arcs;
	delete [] in_uncond;

	return ret;
}


void LPBinaryForks_b::set_general_bounds() {
	const Problem* abs = get_mapping()->get_abstract();
	const vector<int> &doms = abs->get_variable_domains();
	int root_goal = abs->get_goal_val(0);

	for (int v = 1; v < doms.size(); v++) {
		for (int val = 0; val < doms[v]; val++) {
			for (int theta = 0; theta < doms[0]; theta++) {
				int lower_b = 1;
				int upper_b = doms[v];
				// TODO: check if this part is necessary. If the bounds stand for local bounds
				// on sigma size, we probably don't need to increment it here.
				// If the bound is the global bound for achieving the goal from val, then it
				// should be here.
				if (-1 != root_goal){ // There is a goal on the root
					if (theta == root_goal) { //  if the goal is defined and equal to the initial,
						if ((upper_b % 2) == 0)
							upper_b++;
					} else {
						if ((upper_b % 2) == 1)
							upper_b++;
					}
				}
//				cout << "Bounds [" << lower_b << ", " << upper_b << "]" << endl;
				set_sigma_lower_bound(v,val,theta,lower_b);
				set_sigma_upper_bound(v,val,theta,upper_b);
			}
		}
	}
}

int LPBinaryForks_b::get_domain_bound(int v, int g_v, int root_zero) const {
	Mapping* map = get_mapping();
	const Problem* abs = map->get_abstract();
	const vector<Operator*> &ops = abs->get_var_actions(v);

	int root_dom = abs->get_variable_domain(0);  // Should be 2
	int dom = abs->get_variable_domain(v);
	bool **in_arcs = new bool*[dom];
	bool **out_arcs = new bool*[dom];
	bool *in_uncond = new bool[dom];

	for (int val = 0; val < dom; val++){
		in_arcs[val] = new bool[root_dom];
		out_arcs[val] = new bool[root_dom];
		for (int theta = 0; theta < root_dom; theta++){
			in_arcs[val][theta] = false;
			out_arcs[val][theta] = false;
		}
		in_uncond[val] = false;
	}

	for (int a = 0; a < ops.size(); a++) {
		int pre = ops[a]->get_pre_val(v);
		int post = ops[a]->get_post_val(v);
		int prv = ops[a]->get_prevail_val(0);

		int pre_b = (-1 == pre) ? 0 : pre;       // Precondition range
		int pre_e = (-1 == pre) ? dom-1 : pre;

		if (-1 == prv ) { // only in arcs are kept
			in_uncond[post] = true;         // in arc
		} else {
			in_arcs[post][prv] = true;         // in arc

			for (int val = pre_b; val <= pre_e; val++){
				out_arcs[val][prv] = true;    // out arc
			}
		}
	}

	const State* abs_state = abs->get_initial_state();
	const state_var_t * eval_state = abs_state->get_buffer();

	int s_v = (int) eval_state[v];

	cout << "Calculating bounds for variable " << v << " with initial " << s_v << " and goal " << g_v << " under root " << root_zero << endl;
	for (int val = 0; val < dom; val++)
		cout << in_arcs[val][0];
	cout << endl;
	for (int val = 0; val < dom; val++)
		cout << in_arcs[val][1];
	cout << endl;
	for (int val = 0; val < dom; val++)
		cout << out_arcs[val][0];
	cout << endl;
	for (int val = 0; val < dom; val++)
		cout << out_arcs[val][1];
	cout << endl;
	for (int val = 0; val < dom; val++)
		cout << in_uncond[val];
	cout << endl;
	for (int val = 0; val < dom; val++)
		cout << "-";
	cout << endl;

	int ret = 1;  // we start with one, counting the size of the support, and not the number
	// of value changes.
	// if you can go in under one theta, and out under another, the value is counted.
	// for initial value, if you can go out with non-root-zero, then count
	for (int val = 0; val < dom; val++){
		if (val == s_v) {
			if (out_arcs[val][1-root_zero]) {
				ret++;
				cout << "1";
			} else
				cout << " ";
		} else if (val != g_v) { // nothing to count for goal value
			if ((in_arcs[val][0] && out_arcs[val][1]) ||
				(in_arcs[val][1] && out_arcs[val][0]) ||
				(in_uncond[val] && ( out_arcs[val][0] || out_arcs[val][1]))) {
				ret++;
				cout << "1";
			} else
				cout << " ";
		} else cout << " ";
	}
	cout << endl;
	// Deallocating memory for arcs arrays
	for (int val = 0; val < dom; val++){
		delete [] in_arcs[val];
		delete [] out_arcs[val];
	}
	delete [] in_arcs;
	delete [] out_arcs;
	delete [] in_uncond;

	return ret;
}

void LPBinaryForks_b::set_static_constraints() {

	const Problem* abs = get_mapping()->get_abstract();
	const vector<int> &doms = abs->get_variable_domains();

	//For each leaf v (the first variable is always the root)
	int var_num = doms.size();
	for (int v = 1; v < var_num; v++) {
		int dom_size = doms[v];
		// For each value val_0 in Domain(v)
		for (int val_0=0; val_0 < dom_size; val_0++){
			for (int theta=0; theta < doms[0]; theta++){
				// (III) - Static
				// p(v, val_0, val_0, theta) = 0
				int p_ind = p_var(v,val_0,val_0,theta);
				static_LPConstraints.push_back(set_x_eq_0_constraint(p_ind, true));
			}
		}

		const vector<Operator*> &A_v = abs->get_var_actions(v);

		int A_v_size = A_v.size();
		int ***actions = new int**[doms[0]];
//		int actions[doms[0]][doms[v]][doms[v]];
		for (int theta=0; theta < doms[0]; theta++){
			actions[theta] = new int*[dom_size];
			for (int val_0=0; val_0 < dom_size; val_0++){
				actions[theta][val_0] = new int[dom_size];
				for (int val_1=0; val_1 < dom_size; val_1++){
					actions[theta][val_0][val_1] = 0;
				}
			}
		}

		for (int a = 0; a < A_v_size; a++) {
			int prv = A_v[a]->get_prevail_val(0);
			int pre = A_v[a]->get_pre_val(v);
			int post = A_v[a]->get_post_val(v);
			int w_ind0 = w_var(A_v[a]);
			// If precondition is undefined, then there is no need for an auxiliary cost variable.
			if (-1 == pre) { // enter the constraints
				// p(v, val_0, post(a)[v], prv(a)[r]) <= w(a)
				for (int val_0=0; val_0 < dom_size; val_0++){
					int prv_b = (-1 == prv) ? 0 : prv;
					int prv_e = (-1 == prv) ? 1 : prv;

					for (int theta=prv_b; theta <= prv_e; theta++){
						static_LPConstraints.push_back(set_p_constraint(v,val_0,pre,post,theta,w_ind0, true));
					}
				}
			} else { // it can be worth to add an auxiliary variable for a set of actions
				if (-1 == prv) {
					actions[0][pre][post]++;
					actions[1][pre][post]++;
				} else {
					actions[prv][pre][post]++;
				}
			}
		}

		int threshold = 3;
		// Go over the actions again (only those with precondition defined)
		// and add a constraint for each action that has more than threshold similar actions
		// and a regular constraint for the rest.
		for (int a = 0; a < A_v_size; a++) {
			int pre = A_v[a]->get_pre_val(v);
			if (-1 == pre)
				continue;

			int prv = A_v[a]->get_prevail_val(0);
			int post = A_v[a]->get_post_val(v);
			int w_ind0 = w_var(A_v[a]);
			int prv_b = (-1 == prv) ? 0 : prv;
			int prv_e = (-1 == prv) ? 1 : prv;

			for (int theta=prv_b; theta <= prv_e; theta++){
				if (actions[theta][pre][post] > threshold) {
					//assert(false);
					// w(pre,post,prv) <= w(a)
					int w_ind = w_v(v,pre,post,theta);
					static_LPConstraints.push_back(set_x_leq_y_constraint(w_ind,w_ind0,true));
				} else {
					// p(v, val_0, post(a)[v], 0/1) <= p(v, val_0, pre(a)[v], 0/1) + w(a)
					for (int val_0=0; val_0 < dom_size; val_0++){
						static_LPConstraints.push_back(set_p_constraint(v,val_0,pre,post,theta,w_ind0, true));
					}
				}
			}
		}
		// Now add a constraint for each action above threshold
		for (int val_0=0; val_0 < dom_size; val_0++){
			for (int val_1=0; val_1 < dom_size; val_1++){
				for (int theta=0; theta < doms[0]; theta++){
					if (actions[theta][val_0][val_1] > threshold) {
						//assert(false);
						for (int val=0; val < dom_size; val++){
							// (III) - Static cont.
							// p(v, val, post, prv) <= p(v, val, pre, prv) + w(pre, post, prv)
							int w_ind = w_v(v,val_0,val_1,theta);
							static_LPConstraints.push_back(set_p_constraint(v,val,val_0,val_1,theta,w_ind,true));
						}
					}
				}
			}
		}
		// Deallocating actions array
		for (int theta=0; theta < doms[0]; theta++){
			for (int val_0=0; val_0 < dom_size; val_0++){
				delete [] actions[theta][val_0];
			}
			delete [] actions[theta];
		}
		delete [] actions;
	}

	const vector<Operator*> &A_r = abs->get_var_actions(0);
    int w_ind0 = w_r(0);
    int w_ind1 = w_r(1);

	// Dividing root changing actions into two sets, by the post value
	for (int a = 0; a < A_r.size(); a++){
		// If the action does nothing...
		if (A_r[a]->get_pre_val(0) == A_r[a]->get_post_val(0))
			continue;

		if (0 != A_r[a]->get_post_val(0)){
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


void LPBinaryForks_b::get_dynamic_constraints(const State* state, vector<LPConstraint*> &dyn_constr) {

	set_bounds_for_state(state);

	Mapping* map = get_mapping();
	const Problem* abs = map->get_abstract();
	const State* abs_state = map->get_abs_state(state);

	const vector<int> &doms = abs->get_variable_domains();

	const state_var_t * eval_state = abs_state->get_buffer();
	int root_zero = (int) eval_state[0];
/*
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
//		int upper_v = get_domain_bound(v, val, eval_state);
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
*/
	LPBinaryFork::get_dynamic_constraints(state,dyn_constr);
	// (II).1
	//For each leaf v (the first variable is always the root)

	for (int v = 1; v <= num_leafs; v++) {
		int dom_size = doms[v];
		int s_v = eval_state[v];

		// For each value val_0 in Domain(v)
		for (int val_0=0; val_0 < dom_size; val_0++){
			// d(v, val_0, 1) = p(v, s[v], val_0, s[r])
			if (1 == get_sigma_lower_bound(v,val_0,root_zero)) {
				dyn_constr.push_back(set_d_constraint(v,val_0,s_v,1,root_zero,false));
			}

			// For each possible support size, starting with at least 2, up to maximum needed
			int first_support = max(get_sigma_lower_bound(v, val_0, root_zero),2);
			int last_support = get_sigma_upper_bound(v, val_0, root_zero);
//			int last_support = get_domain_bound(v, val_0, eval_state);

			for (int sz=first_support; sz <= last_support; sz++){
				// (II) - Dynamic
				// For each value val_1 in Domain(v)
				for (int val_1=0; val_1 < dom_size; val_1++){
					// d(v, val_0, sz) <= d(v, val_1, sz-1) + p(v, val_1, val_0, 0/1)
					if (get_sigma_lower_bound(v,val_1,root_zero) >= sz)
						continue;
					dyn_constr.push_back(set_d_constraint(v,val_0,val_1,sz,root_zero,false));
				}
			}
		}
	}
}


LPConstraint* LPBinaryForks_b::set_d_constraint(int v, int val_0, int val_1, int sz, int root_zero, bool tokeep) const {
	assert(sz > 0);
	// d(v, val_0, sz) <= d(v, val_1, sz-1) + p(v, val_1, val_0, 0/1)
	int d_ind0 = d_var(v,val_0,sz);
	int p_ind = p_var(v,val_1,val_0,(1+root_zero+sz)%2);

	if (sz > 1) {
		int upper_b = min(get_sigma_upper_bound(v,val_1,root_zero),sz-1);
		int d_ind1 = d_var(v,val_1,upper_b);
		return set_x_leq_y_plus_z_constraint(d_ind0, d_ind1, p_ind, tokeep);
	}
	return set_x_eq_y_constraint(d_ind0, p_ind, tokeep);
}




LPConstraint* LPBinaryForks_b::set_p_constraint(int v, int val, int pre, int post, int prv, int w_ind, bool tokeep) const {
	assert(prv != -1);
	// p(v, val, post, prv) <= p(v, val pre, prv) + w(a)
	int p_ind0 = p_var(v,val,post,prv);
	if (-1 != pre) {
		int p_ind1 = p_var(v,val,pre,prv);
		return set_x_leq_y_plus_z_constraint(p_ind0, p_ind1, w_ind, tokeep);
	}
	// if pre is -1, meaning any value, then p(v, val_0, post(a)[v], prv) <=  w(a)
	return set_x_leq_y_constraint(p_ind0, w_ind, tokeep);
}

LPConstraint* LPBinaryForks_b::set_h_constraint(int sigma, const state_var_t * eval_state) const {

	int root_zero = (int) eval_state[0];
	return set_h_constraint(sigma, root_zero, false);
}


LPConstraint* LPBinaryForks_b::set_h_constraint(int sigma, int root_zero, bool tokeep) const {

	const Problem* abs = get_mapping()->get_abstract();
	// (I) Dynamic
	// h <= cost of root changing actions + sum of d(v,G[v],|sigma|)

	LPConstraint* lpc = new LPConstraint(0.0,DBL_MAX,tokeep);

	int h_ind = h_var();
	lpc->add_val(h_ind, -1.0);

	//For each leaf v (the first variable is always the root)
	for (int v = 1; v <= num_leafs; v++) {
		int g_v = abs->get_goal_val(v);
		int fixed = min(get_sigma_upper_bound(v,g_v,root_zero),sigma);
//		cout << "Sigma " << sigma << " upper " << get_sigma_upper_bound(v,g_v,root_zero) << endl;
		assert(fixed > 0);
		int d_ind = d_var(v,g_v,fixed);
//		int d_ind = d_var(v,g_v,sigma);
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

/*
int LPBinaryForks_b::d_var(int var, int val, int i, int ) const {
	return BinaryFork::d_var(var,val,i);
}
*/

// index for dummy variable for action
int LPBinaryForks_b::w_v(int var, int val1, int val2, int root_val) const {
	int ret = number_of_d_variables + number_of_p_variables + number_of_h_variables +
	number_of_w_r_variables +
	num_leafs*sigma_size*sigma_size*root_val +
	(var-1)*sigma_size*sigma_size + val1*sigma_size + val2;
//	cout << "x_" << ret << " = w_v(v_" << var << "," << val1 << "," << val2 << "," << root_val << ")" << endl;
	return ret;
}

