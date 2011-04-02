#include "SP_globals.h"
#include "LP_binary_forks_off.h"
#include "mapping.h"
#include <math.h>

LPBinaryForks_OFF::LPBinaryForks_OFF() {
	abstraction = new BinaryForksAbstraction();

}

LPBinaryForks_OFF::LPBinaryForks_OFF(GeneralAbstraction* abs) {
	abstraction = abs;

}

LPBinaryForks_OFF::~LPBinaryForks_OFF() {

	for (int i=0; i < static_LPConstraints.size();i++) {
		delete static_LPConstraints[i];
	}
}

void LPBinaryForks_OFF::initiate() {

	const Problem* abs = get_mapping()->get_abstract();
	const vector<int> &doms = abs->get_variable_domains();

	int max_domain_size = 0;

	num_leafs = doms.size() - 1;
	if (0 == num_leafs){
		sigma_size = 2;
		return;
	}

	for (int i = 1; i<=num_leafs; i++)
		if (max_domain_size < doms[i])
			max_domain_size = doms[i];

	sigma_size = max_domain_size+1;

	set_solution(new Solution());

}

void LPBinaryForks_OFF::solve( ) {

	const Problem* abs = get_mapping()->get_abstract();
	const vector<int> &doms = abs->get_variable_domains();

//	int numLPvars = get_num_LP_vars();
	int numLPvars = get_num_vars();
	double* sol = new double[numLPvars];

	//For each leaf v (the first variable is always the root)
	int var_num = doms.size();
	for (int v = 1; v < var_num; v++) {

		int dom_size = doms[v];
		int g_v = abs->get_goal_val(v);
		const vector<Operator*> &A_v = abs->get_var_actions(v);

		int A_v_size = A_v.size();

		for (int val0=0;val0<dom_size;val0++) {
			for (int val1=0;val1<dom_size;val1++) {
				int p_ind0 = p_var(v,val0,val1,0);
				int p_ind1 = p_var(v,val0,val1,1);
				if (val0 == val1) {
					sol[p_ind0] = 0.0;
					sol[p_ind1] = 0.0;
				} else {
					sol[p_ind0] = LP_INFINITY;
					sol[p_ind1] = LP_INFINITY;
				}
			}
		}

		// Initial cost matrix
		for (int a = 0; a < A_v_size; a++) {
			int prv = A_v[a]->get_prevail_val(0);
			int pre = A_v[a]->get_pre_val(v);
			int post = A_v[a]->get_post_val(v);
			//int w_ind = w_var(A_v[a]);
			double c = A_v[a]->get_double_cost();

			if (-1 == pre) {
				for (int val=0;val<dom_size;val++) {
					if (val != post) {
						if (-1 == prv) {
							int p_ind0 = p_var(v,val,post,0);
							int p_ind1 = p_var(v,val,post,1);
							sol[p_ind0] = min(sol[p_ind0],c);
							sol[p_ind1] = min(sol[p_ind1],c);
						} else {
							int p_ind = p_var(v,val,post,prv);
							sol[p_ind] = min(sol[p_ind],c);
						}
					}
				}
			} else {
				if (-1 == prv) {
					int p_ind0 = p_var(v,pre,post,0);
					int p_ind1 = p_var(v,pre,post,1);
					sol[p_ind0] = min(sol[p_ind0],c);
					sol[p_ind1] = min(sol[p_ind1],c);
				} else {
					int p_ind = p_var(v,pre,post,prv);
					sol[p_ind] = min(sol[p_ind],c);
				}
			}
		}

		//Calculating shortest paths
		for (int k=0;k<dom_size;k++) {
			for (int i=0;i<dom_size;i++) {
				for (int j=0;j<dom_size;j++) {
					int p_indij0 = p_var(v,i,j,0);
					int p_indik0 = p_var(v,i,k,0);
					int p_indkj0 = p_var(v,k,j,0);
					int p_indij1 = p_var(v,i,j,1);
					int p_indik1 = p_var(v,i,k,1);
					int p_indkj1 = p_var(v,k,j,1);

					sol[p_indij0] = min(sol[p_indij0],sol[p_indik0] + sol[p_indkj0]);
					sol[p_indij1] = min(sol[p_indij1],sol[p_indik1] + sol[p_indkj1]);
				}
			}
		}

		// Setting the initial values for dynamic calculation of d() variables
		for (int val_0=0; val_0 < dom_size; val_0++){
			for (int theta=0;theta<=1;theta++){
				// d(v, val_0, 1, theta) = p(v, val_0, G'[v], theta)
				int d_ind = d_var(v,val_0,1,theta);
				int p_ind = p_var(v,val_0,g_v,theta);
				sol[d_ind] = sol[p_ind];
			}
		}

		// Making the step calculation
		for (int sz=2; sz <= dom_size+1; sz++){
			for (int val_0=0; val_0 < dom_size; val_0++){
				for (int theta=0;theta<=1;theta++){
					int d_ind = d_var(v,val_0,sz,theta);
					double min_val = LP_INFINITY;
					// d(v, val_0, sz, theta) <= d(v, val_1, sz-1,1-theta) + p(v, val_0, val_1, theta)
					for (int val_1=0; val_1 < dom_size; val_1++){
						int d_ind1 = d_var(v,val_1,sz-1,1-theta);
						int p_ind1 = p_var(v,val_0,val_1,theta);
						double res = sol[d_ind1] + sol[p_ind1];
						if (min_val > res)
							min_val = res;
					}
					sol[d_ind] = min_val;
				}
			}
		}
		// Making the extra step
		for (int sz=dom_size+2; sz <= sigma_size; sz++){
			for (int val_0=0; val_0 < dom_size; val_0++){
				for (int theta=0;theta<=1;theta++){
					// d(v, val_0, sz,theta) = d(v, val_0, sz-1,theta)
					int d_ind20 = d_var(v,val_0,sz,theta);
					int d_ind21 = d_var(v,val_0,sz-1,theta);
					sol[d_ind20] = sol[d_ind21];
				}
			}
		}
	}

	const vector<Operator*> &A_r = abs->get_var_actions(0);

	// Dividing root changing actions into two sets, by the post value
	double min0 = DBL_MAX;
	double min1 = DBL_MAX;

	for (int a = 0; a < A_r.size(); a++) {
		double c = A_r[a]->get_double_cost();
		if (0 == A_r[a]->get_post_val(0)) {
			min0 = min(min0,c);
		} else {
			min1 = min(min1,c);
		}
	}

	int w_ind0 = w_r(0);
	int w_ind1 = w_r(1);

	sol[w_ind0] = min0;
	sol[w_ind1] = min1;

	solution->set_solution(sol,numLPvars);

}


double LPBinaryForks_OFF::get_solution_value(const State* state) {

	Mapping* map = get_mapping();
//	const Problem* abs = map->get_abstract();
	const State* abs_state = map->get_abs_state(state);
//	const vector<int> &doms = abs->get_variable_domains();
	const state_var_t * eval_state = abs_state->get_buffer();
	double min_sol = DBL_MAX;

	for (int sigma = 1; sigma<=sigma_size; sigma++ ) {
		double sol = get_h_val(sigma,eval_state);
		if (min_sol > sol) {
			min_sol = sol;
		}
	}

	return min_sol;
}





double LPBinaryForks_OFF::get_h_val(int sigma, const state_var_t * eval_state) const {

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
	for (int v = 1; v <= num_leafs; v++) {
		int val = (int) eval_state[v];
		int d_ind = d_var(v,val,sigma,root_zero);
		double s =solution->get_value(d_ind);
		if (s >= LP_INFINITY)
			return s;
		sol += s;
	}
	return sol;
}


int LPBinaryForks_OFF::d_var(int var, int val, int i, int theta) const {
	int ret = theta*num_leafs*sigma_size*sigma_size +
			  (var-1)*sigma_size*sigma_size + (i-1)*sigma_size + val;
//	cout << "x_" << ret << " == d(v_" << var << "," << val << "," << i << "," << theta << ")" << endl;
	return ret;
}

int LPBinaryForks_OFF::p_var(int var, int val1, int val2, int root_val) const {
	int ret = num_leafs*sigma_size*sigma_size*(2+root_val) +
			  (var-1)*sigma_size*sigma_size + val1*sigma_size + val2;
//	cout << "x_" << ret << " == p(v_" << var << "," << val1 << "," << val2 << "," << root_val << ")" << endl;
	return ret;
}

int LPBinaryForks_OFF::h_var() const {
	int ret = 4*num_leafs*sigma_size*sigma_size;
//	cout << "x_" << ret << " == h" << endl;
	return ret;
}

int LPBinaryForks_OFF::w_r(int root_zero) const {
	int ret = 4*num_leafs*sigma_size*sigma_size + root_zero + 1;
//	cout << "x_" << ret << " == w_" << root_zero << endl;
	return ret;
}

int LPBinaryForks_OFF::w_var(Operator* a) const {
	const Problem* abs = get_mapping()->get_abstract();
	int ret = 4*num_leafs*sigma_size*sigma_size + 3 + abs->get_action_index(a);
//	cout << "x_" << ret << " == w_a, a:";
//	a->dump();
	return ret;
}

int LPBinaryForks_OFF::get_num_vars() const {
	const Problem* abs = get_mapping()->get_abstract();
	int ret = 4*num_leafs*sigma_size*sigma_size + 3 + abs->get_actions_number();
//	cout << "Number of variables : " << ret << endl;

	return ret;
}

void LPBinaryForks_OFF::dump() const {

	cout << "LP formulation for offline binary fork" << endl << "Objective function:" << endl << "max " ;
	for (int i = 0; i < obj_func->get_vals().size(); i++)
		cout << " + " << obj_func->get_vals()[i]->val << " * x_" << obj_func->get_vals()[i]->var;
	cout << endl;

	cout << "Static Constraints:" << endl;
	for (int i = 0; i < static_LPConstraints.size(); i++)
		static_LPConstraints[i]->dump();

}

