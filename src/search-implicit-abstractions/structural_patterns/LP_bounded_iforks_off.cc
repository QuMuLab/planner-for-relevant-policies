#include "SP_globals.h"
#include "LP_bounded_iforks_off.h"
#include "mapping.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "LP_heuristic.h"

LPBoundedIforks_OFF::LPBoundedIforks_OFF() :LPBoundedIfork() {
}

LPBoundedIforks_OFF::LPBoundedIforks_OFF(GeneralAbstraction* abs) :LPBoundedIfork(abs) {
}
LPBoundedIforks_OFF::LPBoundedIforks_OFF(IforksAbstraction* ifork, Domain* abs_domain) :LPBoundedIfork(ifork,abs_domain) {
}

LPBoundedIforks_OFF::~LPBoundedIforks_OFF() {
}
/*
void LPBoundedIforks_OFF::initiate() {

	const Problem* abs = get_mapping()->get_abstract();

	const vector<int> &doms = abs->get_variable_domains();

	max_domain = 0;
	num_parents = doms.size() - 1;

	int root_dom = doms[0];
	for (int i = 1; i<=num_parents; i++)
		if (max_domain < doms[i])
			max_domain = doms[i];

	root_paths_vals = new vector<IforkRootPath*>[root_dom];
	int root_goal = abs->get_goal_val(0);

	vector<vector<Operator*> > paths;
//	abs->get_cycle_free_paths_by_length(0, root_dom-1, paths);
	abs->get_all_cycle_free_paths_to_goal(0, paths);
	for (int i = 0; i < paths.size(); i++) {
		vector<Operator*> path = paths[i];
		IforkRootPath* new_path = new IforkRootPath(doms.size());
		new_path->set_path(path);
		all_root_paths_vals.push_back(new_path);

		int val = path[0]->get_pre_val(0);
		if (-1 == val) {
			// Adding the path to all values except the values on the path.
			vector<int> vals_on_path;
			vals_on_path.assign(root_dom,-1);
			for (int p=0; p < path.size(); p++) {
				vals_on_path[path[p]->get_post_val(0)] = 0;
			}

			for (int j=0; j < root_dom; j++) {
				if (vals_on_path[j] != 0){
					root_paths_vals[j].push_back(new_path);
				}
			}
		} else {
			root_paths_vals[val].push_back(new_path);
		}
	}
	vector<Operator*> emp_path;
	IforkRootPath* empty_path = new IforkRootPath(doms.size());
	empty_path->set_path(emp_path);

	all_root_paths_vals.push_back(empty_path);
	root_paths_vals[root_goal].push_back(empty_path);
}
*/

void LPBoundedIforks_OFF::set_objective(){
	cout << "LPBoundedIforks_OFF::set_objective()" << endl;
	const Problem* abs = get_mapping()->get_abstract();
	const vector<int> &doms = abs->get_variable_domains();
	obj_func = new LPConstraint();

	//For each leaf v (the first variable is always the root)
	// sum_{v\in V', val_0, val_1\in\domain(v)}  d(v, val_0, val_1)
	int var_num = doms.size();
	for (int v = 1; v < var_num; v++) {
		int dom_size = doms[v];

		// For each value val_0 in Domain(v)
		for (int val_0=0; val_0 < dom_size; val_0++){
			for (int val_1=0; val_1 < dom_size; val_1++){
				if (val_0!=val_1) {
					int d_ind = d_var(v,val_0,val_1);
					obj_func->add_val(d_ind, 1.0);
				}
			}
		}
	}
	obj_func->finalize();
}



/*

void LPBoundedIforks_OFF::solve() {

	set_solution(new Solution());
	const Problem* abs = get_mapping()->get_abstract();
	const vector<int> &doms = abs->get_variable_domains();

//	int numLPvars = get_num_LP_vars();
	int numLPvars = get_num_vars();
	double* sol = new double[numLPvars];

	//For each parent v (the first variable is always the root)
	int var_num = doms.size();
	for (int v = 1; v < var_num; v++) {
		int dom_size = doms[v];
		const vector<Operator*> &A_v = abs->get_var_actions(v);

		int A_v_size = A_v.size();

		for (int val0=0;val0<dom_size;val0++) {
			for (int val1=0;val1<dom_size;val1++) {
				int d_ind = d_var(v,val0,val1);
				if (val0 == val1) {
					sol[d_ind] = 0.0;
				} else {
					sol[d_ind] = LP_INFINITY;
				}
			}
		}

		// Initial cost matrix
		for (int a = 0; a < A_v_size; a++) {
			int pre = A_v[a]->get_pre_val(v);
			int post = A_v[a]->get_post_val(v);
			double c = A_v[a]->get_double_cost();

			if (-1 == pre) {
				// if pre is -1, meaning any value, then
				// d(v, val, post(a)[v]) <=  w(a)
				for (int val=0;val<dom_size;val++) {
					if (val != post) {
						int d_ind = d_var(v,val,post);
						sol[d_ind] = min(sol[d_ind],c);
					}
				}
			} else {
				// d(v, val_0, post(a)[v]) <= d(v, val_0, pre(a)[v]) + w(a)
				int d_ind = d_var(v,pre,post);
				sol[d_ind] = min(sol[d_ind],c);
			}
		}

		//Calculating shortest paths
		for (int k=0;k<dom_size;k++) {
			for (int i=0;i<dom_size;i++) {
				for (int j=0;j<dom_size;j++) {
					int d_indij = d_var(v,i,j);
					int d_indik = d_var(v,i,k);
					int d_indkj = d_var(v,k,j);

					sol[d_indij] = min(sol[d_indij],sol[d_indik] + sol[d_indkj]);
				}
			}
		}
	}

	solution->set_solution(sol,numLPvars);

	delete [] sol;
}
*/
void LPBoundedIforks_OFF::set_static_constraints() {

	const Problem* abs = get_mapping()->get_abstract();
	const vector<int> &doms = abs->get_variable_domains();

	//For each parent v (the first variable is always the root)
	int var_num = doms.size();
	for (int v = 1; v < var_num; v++) {
		int dom_size = doms[v];
		const vector<Operator*> &A_v = abs->get_var_actions(v);

		int A_v_size = A_v.size();

		// For each value val_0 in Domain(v)
		for (int val_0=0; val_0 < dom_size; val_0++){
			// (II) - Static
			// d(v, val_0, val_0) = 0
			int d_ind0 = d_var(v,val_0,val_0);
			static_LPConstraints.push_back(set_x_eq_0_constraint(d_ind0, true));
			// (II) - Static cont.
			for (int a = 0; a < A_v_size; a++) {
				int pre = A_v[a]->get_pre_val(v);
				int post = A_v[a]->get_post_val(v);
				double c = A_v[a]->get_double_cost();

				LPConstraint* lpc1;
				if (-1 == pre) {
					// if pre is -1, meaning any value, then
					// d(v, val_0, post(a)[v]) <=  w(a)

					lpc1 = new LPConstraint(0.0,c,true);
				} else {
					// d(v, val_0, post(a)[v]) <= d(v, val_0, pre(a)[v]) + w(a)

					lpc1 = new LPConstraint(-DBL_MAX,c,true);

					int d_ind1 = d_var(v,val_0,pre);
					lpc1->add_val(d_ind1, -1.0);
				}
				int d_ind0 = d_var(v,val_0,post);
				lpc1->add_val(d_ind0, 1.0);

				lpc1->finalize();
				static_LPConstraints.push_back(lpc1);
			}
		}
	}
}


///////////////////////////////////////////////////////////////////////////////////////////////

/*

void LPBoundedIforks_OFF::set_solution(Solution* sol) {
	solution = sol;

	int all_paths = all_root_paths_vals.size();
	for (int i=0;i<all_paths;i++) {
		precalculate_path(all_root_paths_vals[i]);
	}
}

void LPBoundedIforks_OFF::precalculate_path(IforkRootPath* path) {

	const Problem* abs = get_mapping()->get_abstract();
	const vector<int> &doms = abs->get_variable_domains();

	// Adding the path cost
	double sol = path->get_path_cost();

	int num_vars = doms.size();
	for (int v = 1; v < num_vars; v++) {
		vector<int> supp;
		path->get_path_support(v,supp);
		int g_v = abs->get_goal_val(v);
		if (-1 != g_v) {
			supp.push_back(g_v);
		}
		if (supp.size() > 0) {
			path->set_first_needed(v,supp[0]);
		}
		sol += calculate_supp_cost(v,supp);
	}
	path->set_needed_cost(sol);
}

double LPBoundedIforks_OFF::calculate_supp_cost(int v, vector<int>& supp) {
	double sol = 0.0;
	for (int i = 1; i < supp.size(); i++) {
		int d_ind = d_var(v,supp[i-1],supp[i]);
		sol += solution->get_value(d_ind);
	}
	return sol;
}

double LPBoundedIforks_OFF::get_solution_value(const State* state) {

	Mapping* map = get_mapping();
	const Problem* abs = map->get_abstract();
	const State* abs_state = map->get_abs_state(state);
	const vector<int> &doms = abs->get_variable_domains();
	const state_var_t * eval_state = abs_state->get_buffer();
	int root_zero = (int) eval_state[0];
	int num_vars = doms.size();
	vector<IforkRootPath*> paths = root_paths_vals[root_zero];

	double min_sol = DBL_MAX;

	int num_paths = paths.size();
	// For each cycle free path:
	for (int p = 0; p < num_paths; p++) {
		IforkRootPath* path = paths[p];

		double sol = path->get_needed_cost();

		for (int v = 1; v < num_vars; v++) {
			int from = (int) eval_state[v];
			int to = path->get_first_needed(v);

			if ((-1 != to) && (from != to)) {
				int d_ind = d_var(v,from,to);
				sol += solution->get_value(d_ind);
			}
		}
		if (min_sol > sol) {
			min_sol = sol;
		}
	}
	return min_sol;
}

int LPBoundedIforks_OFF::d_var(int var, int val_0, int val_1) const {
	int ret = (var-1)*max_domain*max_domain + val_0*max_domain + val_1;
//	cout << "x_" << ret << " = d(v_" << var << "," << val_0 << "," << val_1 << ")" << endl;
	return ret;
}
*/
