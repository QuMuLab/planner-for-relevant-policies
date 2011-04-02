#include "LP_binary_forks_KD.h"
#include "mapping.h"
#include <math.h>


LPBinaryForks_KD::LPBinaryForks_KD() :LPBinaryFork() {
	set_d_vars_multiplier(1);
}

LPBinaryForks_KD::LPBinaryForks_KD(GeneralAbstraction* abs) :LPBinaryFork(abs) {
	set_d_vars_multiplier(1);
}

LPBinaryForks_KD::~LPBinaryForks_KD() {
}


void LPBinaryForks_KD::set_static_constraints() {

	const Problem* abs = get_mapping()->get_abstract();
	const vector<int> &doms = abs->get_variable_domains();

	//For each leaf v (the first variable is always the root)
	int var_num = doms.size();
	for (int v = 1; v < var_num; v++) {
		int dom_size = doms[v];
		const vector<Operator*> &A_v = abs->get_var_actions(v);

		int A_v_size = A_v.size();

		// For each value val_0 in Domain(v)
		for (int val_0=0; val_0 < dom_size; val_0++){
			for (int theta=0; theta < doms[0]; theta++){
				// (III) - Static
				// p(v, val_0, val_0, 0) = 0, p(v, val_0, val_0, 1) = 0
				int p_ind = p_var(v,val_0,val_0,theta);
				static_LPConstraints.push_back(set_x_eq_0_constraint(p_ind, true));

				// (II) - Dynamic
				// For each value val_1 in Domain(v)
				for (int val_1=0; val_1 < dom_size; val_1++){
					// For each 1 < sz <= |\sigma(r)|
					for (int sz=2; sz <= dom_size+1; sz++){
						// d(v, val_1, sz) <= d(v, val_0, sz-1) + p(v, val_1, val_0, 0/1)
						int d_ind0 = d_var(v,val_1,sz);
						int d_ind1 = d_var(v,val_0,sz-1);
						int p_ind0 = p_var(v,val_0,val_1,(sz + theta - 1)%2);
						int p_ind0 = p_var(v,val_0,val_1,1 - (sz%2));
						int p_ind1 = p_var(v,val_0,val_1,sz%2);
						dynamic_LPConstraints[theta].push_back(
								set_x_leq_y_plus_z_constraint(d_ind0, d_ind1, p_ind, true));
					}
					for (int sz=dom_size+2; sz <= sigma_size; sz++){
						// d(v, val_1, sz) = d(v, val_1, sz-1)
						if (val_0 != val_1)
							continue;
						int d_ind0 = d_var(v,val_1,sz);
						int d_ind1 = d_var(v,val_0,sz-1);
						dynamic_LPConstraints[theta].push_back(
								set_x_eq_y_constraint(d_ind0, d_ind1, true));
					}
				}

			}

			// (III) - Static cont.
			for (int a = 0; a < A_v_size; a++) {
				int prv = A_v[a]->get_prevail_val(0);
				int pre = A_v[a]->get_pre_val(v);
				int post = A_v[a]->get_post_val(v);
				int w_ind0 = w_var(A_v[a]);

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



void LPBinaryForks_KD::get_dynamic_constraints(const State* state, vector<LPConstraint*> &dyn_constr) {

	LPBinaryFork::get_dynamic_constraints(state, dyn_constr);

	// (II).1
	//For each leaf v (the first variable is always the root)

	for (int v = 1; v <= num_leafs; v++) {
		int dom_size = doms[v];
		int s_v = eval_state[v];
		// For each value val_0 in Domain(v)
		for (int val_0=0; val_0 < dom_size; val_0++){
			// d(v, val_0, 1) <= p(v, s[v], val_0, s[r])
			int d_ind0 = d_var(v,val_0,1);
			int p_ind0 = p_var(v,s_v,val_0,root_zero);
			dyn_constr.push_back(set_x_leq_y_constraint(d_ind0, p_ind0, false));
		}
	}
}


LPConstraint* LPBinaryForks_KD::set_h_constraint(int sigma) const {
	Mapping* map = get_mapping();
	const Problem* abs = map->get_abstract();
	// (I) Dynamic
	// h <= cost of root changing actions + sum of d(v,G[v],|sigma|)

	LPConstraint* lpc = new LPConstraint(0.0,DBL_MAX,false);

	int h_ind = h_var();
	lpc->add_val(h_ind, -1.0);

	//For each leaf v (the first variable is always the root)
	for (int v = 1; v <= num_leafs; v++) {
		int goal_v = abs->get_goal_val(v);
		int d_ind = d_var(v,goal_v,sigma);
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
