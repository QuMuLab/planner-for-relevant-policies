#include "LP_bounded_ifork_gen.h"
#include "mapping.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "LP_heuristic.h"

LPBoundedIfork::LPBoundedIfork() :BoundedIfork() {
}

LPBoundedIfork::LPBoundedIfork(GeneralAbstraction* abs) :BoundedIfork(abs) {
}

LPBoundedIfork::LPBoundedIfork(IforksAbstraction* ifork, Domain* abs_domain) :BoundedIfork(ifork, abs_domain) {
}

LPBoundedIfork::~LPBoundedIfork() {
}

void LPBoundedIfork::initiate() {
	BoundedIfork::initiate();

	const Problem* abs = get_mapping()->get_abstract();
	const vector<int> &doms = abs->get_variable_domains();

	number_of_h_variables = 1;
	number_of_w_var_variables = abs->get_actions_number();

	int root_dom = doms[0];

	vector<vector<Operator*> > paths;
//	abs->get_cycle_free_paths_by_length(0, root_dom-1, paths);
	abs->get_all_cycle_free_paths_to_goal(0, paths);
	for (int i = 0; i < paths.size(); i++) {
		vector<Operator*> path = paths[i];
		IforkRootPath* new_path = new IforkRootPath(doms.size());
		new_path->set_path(path);
		precalculate_path(new_path);
		vector<int> vals;
		new_path->get_applicable_vals(root_dom,vals);
		assert(0 < vals.size());
		root_paths_values[vals[0]].push_back(new_path);
		for (int j=1; j < vals.size(); j++) {
			root_paths_values[vals[j]].push_back(new IforkRootPath(new_path));
		}
	}
	vector<Operator*> emp_path;
	IforkRootPath* empty_path = new IforkRootPath(doms.size());
	empty_path->set_path(emp_path);
	precalculate_path(empty_path);

	int root_goal = abs->get_goal_val(0);
	root_paths_values[root_goal].push_back(empty_path);
}

void LPBoundedIfork::precalculate_path(IforkRootPath* path) {

	const Problem* abs = get_mapping()->get_abstract();
	const vector<int> &doms = abs->get_variable_domains();

	LPConstraint* lpc0 = new LPConstraint(0.0,DBL_MAX,true);

	// Adding the h variable
	int h_ind = h_var();
	lpc0->add_val(h_ind, -1.0);

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
			for (int i = 1; i < supp.size(); i++) {
				int d_ind = d_var(v,supp[i-1],supp[i]);
				lpc0->add_val(d_ind, 1.0);
			}
		}
	}

	// Adding the w variables
	const vector<Operator*>& ops = path->get_path();
//	vector<Operator*> ops;
//	path->get_path(ops);
	for (int i = 0; i < ops.size(); i++) {
		int w_ind = w_var(ops[i]);
		lpc0->add_val(w_ind, 1.0);
	}
	path->set_LP_constraint(lpc0);

}


void LPBoundedIfork::set_static_constraints() {

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
				int w_ind0 = w_var(A_v[a]);
				if (pre == post)
					continue; // ignore the self loop actions
				// d(v, val_0, post(a)[v]) <= d(v, val_0, pre(a)[v]) + w(a)
				int d_ind0 = d_var(v,val_0,post);

				if (-1 != pre) {
					int d_ind1 = d_var(v,val_0,pre);
					static_LPConstraints.push_back(set_x_leq_y_plus_z_constraint(d_ind0, d_ind1,w_ind0,true));
					continue;
				}
				// if pre is -1, meaning any value, then
				// d(v, val_0, post(a)[v]) <=  w(a)
				static_LPConstraints.push_back(set_x_leq_y_constraint(d_ind0, w_ind0, true));
			}
		}
	}
}



void LPBoundedIfork::get_dynamic_constraints(const State* state, vector<LPConstraint*> &dyn_constr) {

	Mapping* map = 	get_mapping();
	const Problem* abs = map->get_abstract();
	const State* abs_state = map->get_abs_state(state);
	const vector<int> &doms = abs->get_variable_domains();

	const state_var_t * eval_state = abs_state->get_buffer();
	int root_zero = (int) eval_state[0];

	int num_vars = doms.size();

	// For each cycle free path:
	for (int p = 0; p < root_paths_values[root_zero].size(); p++) {
		IforkRootPath* path = root_paths_values[root_zero][p];
		LPConstraint* lpc0 = new LPConstraint(path->get_LP_constraint(),false);

		for (int v = 1; v < num_vars; v++) {
			int from = (int) eval_state[v];
			int to = path->get_first_needed(v);
			if ((-1 != to) && (from != to)) {
				int d_ind = d_var(v,from,to);
				lpc0->add_val(d_ind, 1.0);
			}
		}

		lpc0->finalize();
		// Adding the constraint (not to keep)
		dyn_constr.push_back(lpc0);
	}
}


int LPBoundedIfork::h_var() const {
	int ret = number_of_d_variables;
//	cout << "x_" << ret << " = h" << endl;
	return ret;
}

int LPBoundedIfork::w_var(Operator* a) const {
	const Problem* abs = get_mapping()->get_abstract();
	int ret = number_of_d_variables + number_of_h_variables + abs->get_action_index(a);
//	cout << "x_" << ret << " = w_a, a:";
//	a->dump();
	return ret;
}


