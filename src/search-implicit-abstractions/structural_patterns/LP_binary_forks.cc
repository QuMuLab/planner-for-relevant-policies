#include "LP_binary_forks.h"
#include "mapping.h"
#include <math.h>


LPBinaryForks::LPBinaryForks() :LPBinaryFork() {
}

LPBinaryForks::LPBinaryForks(GeneralAbstraction* abs) :LPBinaryFork(abs){
}

LPBinaryForks::~LPBinaryForks() {
}

void LPBinaryForks::initiate() {
	LPBinaryFork::initiate();
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
/*
void LPBinaryForks::set_static_constraints() {

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
				LPConstraint* lpc0 = new LPConstraint(0.0,0.0,true);
				lpc0->add_val(p_ind,1.0);
				lpc0->finalize();
				static_LPConstraints.push_back(lpc0);

				// (II).1 - Dynamic
				// d(v, val_0, 1, theta) = p(v, val_0, G[v], theta)
				if (lower_bound[bound_ind(v,val_0,theta)] == 1) {
					int d_ind0 = d_var(v,val_0,1,theta);
					int p_ind0 = p_var(v,val_0,g_v,theta);

					LPConstraint* lpc5 = new LPConstraint(0.0,0.0,true);
					lpc5->add_val(d_ind0, -1.0);
					lpc5->add_val(p_ind0, 1.0);
					lpc5->finalize();
					static_LPConstraints.push_back(lpc5);
				}
				// (II).2 - Dynamic
				// For each value val_1 in Domain(v)
				for (int val_1=0; val_1 < dom_size; val_1++){
					// For each 1 < sz <= |\sigma(r)|
					int bind0 = bound_ind(v, val_1,theta);
					int first_support = max(lower_bound[bind0],2);
					for (int sz=first_support; sz <= upper_bound[bind0]; sz++){
						// d(v, val_1, sz, theta) <= d(v, val_0, sz-1, 1-theta) + p(v, val_1, val_0, theta)

						if (lower_bound[bound_ind(v,val_0,1-theta)] >= sz)
							continue;
						int d_ind0 = d_var(v,val_1,sz,theta);
						int upper_b = min(upper_bound[bound_ind(v,val_0,1-theta)],sz-1);
						int d_ind1 = d_var(v,val_0,upper_b,1-theta);
//						int d_ind1 = d_var(v,val_0,sz-1,1-theta);
						int p_ind = p_var(v,val_1,val_0,theta);

						LPConstraint* lpc0 = new LPConstraint(0.0,DBL_MAX,true);
						lpc0->add_val(d_ind0, -1.0);
						lpc0->add_val(d_ind1, 1.0);
						lpc0->add_val(p_ind, 1.0);
						lpc0->finalize();
						static_LPConstraints.push_back(lpc0);
					}
				}
			}
			// (III) - Static cont.
			for (int a = 0; a < A_v_size; a++) {
				int prv = A_v[a]->get_prevail_val(0);
				int pre = A_v[a]->get_pre_val(v);
				int post = A_v[a]->get_post_val(v);
				int w_ind0 = w_var(A_v[a]);

				if (-1 == prv) {

					// p(v, val_0, post(a)[v], 0/1) <= p(v, val_0, pre(a)[v], 0/1) + w(a)
					int p_ind0 = p_var(v,val_0,post,0);
					int p_ind2 = p_var(v,val_0,post,1);
					// New LP Constraints
					LPConstraint* lpc2 = new LPConstraint(0.0,DBL_MAX,true);
					LPConstraint* lpc3 = new LPConstraint(0.0,DBL_MAX,true);

					lpc2->add_val(p_ind0, -1.0);
					lpc3->add_val(p_ind2, -1.0);


					if (-1 != pre) {
						// if pre is -1, meaning any value, then
						// p(v, val_0, post(a)[v], 0/1) <=  w(a)

						int p_ind1 = p_var(v,val_0,pre,0);
						int p_ind3 = p_var(v,val_0,pre,1);

						lpc2->add_val(p_ind1, 1.0);
						lpc3->add_val(p_ind3, 1.0);
					}

					lpc2->add_val(w_ind0, 1.0);
					lpc3->add_val(w_ind0, 1.0);
					lpc2->finalize();
					lpc3->finalize();
					static_LPConstraints.push_back(lpc2);
					static_LPConstraints.push_back(lpc3);

				} else {
					// p(v, val_0, post(a)[v], pre(a)[r]) <= p(v, val_0, pre(a)[v], pre(a)[r]) + w(a)
					int p_ind0 = p_var(v,val_0,post,prv);

					// New LP Constraints
					LPConstraint* lpc4 = new LPConstraint(0.0,DBL_MAX,true);

					lpc4->add_val(p_ind0, -1.0);


					if (-1 != pre) {
						// if pre is -1, meaning any value, then
						// p(v, val_0, post(a)[v], 0/1) <=  w(a)

						int p_ind1 = p_var(v,val_0,pre,prv);
						lpc4->add_val(p_ind1, 1.0);
					}
					lpc4->add_val(w_ind0, 1.0);
					lpc4->finalize();
					static_LPConstraints.push_back(lpc4);
				}
			}
		}
	}

	const vector<Operator*> &A_r = abs->get_var_actions(0);

	// Dividing root changing actions into two sets, by the post value
	vector<Operator*> A_r_0, A_r_1;
	for (int a = 0; a < A_r.size(); a++)
		if (0 != A_r[a]->get_post_val(0))
			A_r_0.push_back(A_r[a]);
		else
			A_r_1.push_back(A_r[a]);

	int Ar0_size = A_r_0.size();
	int Ar1_size = A_r_1.size();

	int w_ind0 = w_r(0);
	int w_ind1 = w_r(1);
	for (int a = 0; a < Ar0_size; a++){
		int w_ind2 = w_var(A_r_0[a]);

		// New LP Constraints
		LPConstraint* lpc0 = new LPConstraint(0.0,DBL_MAX,true);
		LPConstraint* lpc1 = new LPConstraint(0.0,DBL_MAX,true);
		lpc0->add_val(w_ind0, -1.0);
		lpc0->add_val(w_ind2, 1.0);
		lpc1->add_val(w_ind1, -1.0);
		lpc1->add_val(w_ind2, 1.0);
		lpc0->finalize();
		lpc1->finalize();
		dynamic_LPConstraints[0].push_back(lpc0);
		dynamic_LPConstraints[1].push_back(lpc1);
	}
	for (int a = 0; a < Ar1_size; a++) {
		int w_ind3 = w_var(A_r_1[a]);

		// New LP Constraints
		LPConstraint* lpc0 = new LPConstraint(0.0,DBL_MAX,true);
		LPConstraint* lpc1 = new LPConstraint(0.0,DBL_MAX,true);
		lpc0->add_val(w_ind1, -1.0);
		lpc0->add_val(w_ind3, 1.0);
		lpc1->add_val(w_ind0, -1.0);
		lpc1->add_val(w_ind3, 1.0);
		lpc0->finalize();
		lpc1->finalize();
		dynamic_LPConstraints[0].push_back(lpc0);
		dynamic_LPConstraints[1].push_back(lpc1);
	}
}

void LPBinaryForks::get_dynamic_constraints(const State* state, vector<LPConstraint*> &dyn_constr) {

	Mapping* map = get_mapping();
	const Problem* abs = map->get_abstract();
	const State* abs_state = map->get_abs_state(state);
//	const vector<int> &doms = abs->get_variable_domains();
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
		int b_ind = bound_ind(v,val,root_zero);
//		if (STATISTICS >= 2) {
//			cout << " " << upper_bound[b_ind];
//		}
		lower_b = (lower_b < lower_bound[b_ind]) ? lower_bound[b_ind] : lower_b;
		upper_b = (upper_b < upper_bound[b_ind]) ? upper_bound[b_ind] : upper_b;
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


LPConstraint* LPBinaryForks::set_h_constraint(int sigma, const state_var_t * eval_state) const {

	int root_zero = (int) eval_state[0];
	// (I) Dynamic
	// h <= cost of root changing actions + sum of d(v,G[v],|sigma|)
	// h <= cost of root changing actions + sum of d(v,s[v],|sigma|,s[r])

	LPConstraint* lpc = new LPConstraint(0.0,DBL_MAX,false);

	int h_ind = h_var();
	lpc->add_val(h_ind, -1.0);

	//For each leaf v (the first variable is always the root)
	for (int v = 1; v <= num_leafs; v++) {
		int val = (int) eval_state[v];
		int fixed = min(upper_bound[bound_ind(v,val,root_zero)],sigma);
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

int LPBinaryForks::d_var(int var, int val, int i, int theta) const {
	int ret = theta*num_leafs*sigma_size*sigma_size +
			  (var-1)*sigma_size*sigma_size + (i-1)*sigma_size + val;
//	cout << "x_" << ret << " == d(v_" << var << "," << val << "," << i << "," << theta << ")" << endl;
	return ret;
}


int LPBinaryForks::p_var(int var, int val1, int val2, int root_val) const {
	int ret = num_leafs*sigma_size*sigma_size*(2+root_val) +
			  (var-1)*sigma_size*sigma_size + val1*sigma_size + val2 + 2;
//	cout << "x_" << ret << " == p(v_" << var << "," << val1 << "," << val2 << "," << root_val << ")" << endl;
	return ret;
}

int LPBinaryForks::h_var() const {
	int ret = 4*num_leafs*sigma_size*sigma_size;
//	cout << "x_" << ret << " = h" << endl;
	return ret;
}

int LPBinaryForks::w_r(int root_zero) const {
	int ret = 4*num_leafs*sigma_size*sigma_size + 1 + root_zero;
//	cout << "x_" << ret << " == w_" << root_zero << endl;
	return ret;
}

int LPBinaryForks::w_var(Operator* a) const {
	const Problem* abs = get_mapping()->get_abstract();
	int ret = 4*num_leafs*sigma_size*sigma_size + 3 + abs->get_action_index(a);
//	cout << "x_" << ret << " = w_a, a:";
//	a->dump();
	return ret;
}

int LPBinaryForks::get_num_vars() const {
	const Problem* abs = get_mapping()->get_abstract();
	int ret = 4*num_leafs*sigma_size*sigma_size + 3 + abs->get_actions_number();
//	cout << "Number of variables : " << ret << endl;
	return ret;
}


int LPBinaryForks::bound_ind(int var, int val, int theta) const {
	int ret = theta*num_leafs*sigma_size +
	  (var-1)*sigma_size + val;
//	cout << "Lower bound : " << ret << endl;
	return ret;
}

int LPBinaryForks::get_sigma_lower_bound(int var, int val, int theta) const {
	return lower_bound[bound_ind(var, val, theta)];
}

int LPBinaryForks::get_sigma_upper_bound(int var, int val, int theta) const {
	return upper_bound[bound_ind(var, val, theta)];
}


void LPBinaryForks::dump() const {

	cout << "LP formulation for binary fork - see the technical report" << endl;

	cout << "Objective function:" << endl;
	cout << "max " ;
	for (int i = 0; i < obj_func->get_vals().size(); i++)
		cout << " + " << obj_func->get_vals()[i]->val << " * x_" << obj_func->get_vals()[i]->var;
	cout << endl;

	cout << "Static Constraints:" << endl;
	for (int i = 0; i < static_LPConstraints.size(); i++)
		static_LPConstraints[i]->dump();

	cout << "Static Constraints for states with root value 0:" << endl;
	for (int i = 0; i < (dynamic_LPConstraints[0]).size(); i++)
		(dynamic_LPConstraints[0])[i]->dump();

	cout << "Static Constraints for states with root value 1:" << endl;
	for (int i = 0; i < (dynamic_LPConstraints[1]).size(); i++)
		(dynamic_LPConstraints[1])[i]->dump();
}

*/
