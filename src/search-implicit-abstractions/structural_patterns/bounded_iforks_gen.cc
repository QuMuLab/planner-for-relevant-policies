#include "SP_globals.h"
#include "bounded_iforks_gen.h"
#include "mapping.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
//#include "LP_heuristic.h"

BoundedIfork::BoundedIfork() {
	abstraction = new BoundedIforksAbstraction();
}

BoundedIfork::BoundedIfork(GeneralAbstraction* abs) {
	abstraction = abs;
}

BoundedIfork::BoundedIfork(IforksAbstraction* ifork, Domain* abs_domain){
	abstraction = new BoundedIforksAbstraction(ifork, abs_domain);
}

BoundedIfork::~BoundedIfork() {

	const Problem* abs = get_mapping()->get_abstract();
	int root_dom = abs->get_variable_domain(0);

	for (int root_val = 0; root_val < root_dom; root_val++) {
		for (int i=0;i<root_paths_values[root_val].size();i++) {
			delete root_paths_values[root_val][i];
		}
	}
	delete [] root_paths_values;

//	delete solution;
}

void BoundedIfork::initiate() {

	const Problem* abs = get_mapping()->get_abstract();
	const vector<int> &doms = abs->get_variable_domains();

	max_domain = 0;
	num_parents = doms.size() - 1;

	int root_dom = doms[0];
	for (int i = 1; i<=num_parents; i++)
		if (max_domain < doms[i])
			max_domain = doms[i];

	root_paths_values = new vector<IforkRootPath*>[root_dom];

	// Setting the solution
	set_solution(new Solution());

	number_of_d_variables = num_parents*max_domain*max_domain;
	number_of_h_variables = 0;
	number_of_w_var_variables = 0;
}


void BoundedIfork::solve_internal(bool remove_dominating) {
//	cout << "Solving the inverted fork" << endl;
	const Problem* abs = get_mapping()->get_abstract();
	const vector<int> &doms = abs->get_variable_domains();

	// Freed in the end of this function
	double* sol = new double[get_num_vars()];
	solution->clear_solution();
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

			int start_val = (-1 == pre) ? 0 : pre;
			int end_val = (-1 == pre) ? dom_size-1 : pre;

			for (int val=start_val;val<=end_val;val++) {
				if (val != post) {
					int d_ind = d_var(v,val,post);
					sol[d_ind] = min(sol[d_ind],c);
				}
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

	vector<vector<int> > to_keep;
	create_non_dominating_paths(sol, to_keep, remove_dominating);
	// Saving the solution - keeping only the needed values.
	for (int v = 1; v < doms.size(); v++) {
		for (int to_val = 0; to_val< doms[v]; to_val++) {
			if (-1 != to_keep[v][to_val]) {
				for (int from_val = 0; from_val< doms[v]; from_val++) {
					if (from_val != to_val) {
						int d_ind = d_var(v,from_val,to_val);
						solution->set_value(d_ind,sol[d_ind]);
					}
				}
			}
		}
	}
//	cout << "Done Solving the inverted fork" << endl;
//	solution->dump();
	// Freeing the allocated temporal solution array.
	delete [] sol;

}

bool compare_IforkRootPath (IforkRootPath* first, IforkRootPath* second)
{
	return first->get_needed_cost() < second->get_needed_cost();
}

void BoundedIfork::create_non_dominating_paths(double* sol, vector<vector<int> >& to_keep, bool remove_dominating){
	////////////////////////////////////////////////////////////////////////////////
	// Calculate the paths and order increasingly by the cost
	// For each root value a new path is created, then all paths are sorted by their costs
	// and the dominating paths are deleted.

	const Problem* abs = get_mapping()->get_abstract();
	const vector<int> &doms = abs->get_variable_domains();

	int root_dom = doms[0];
	int root_goal = abs->get_goal_val(0);

	list<IforkRootPath*>* root_paths_vals = new list<IforkRootPath*>[root_dom];

	vector<vector<Operator*> > paths;
//	abs->get_cycle_free_paths_by_length(0, root_dom - 1, paths);
	abs->get_all_cycle_free_paths_to_goal(0, paths);
	// TODO: instead of copying the paths, implement another way of removing the dominating paths
	int num_paths = paths.size();
	for (int i = 0; i < num_paths; i++) {
		vector<Operator*> path = paths[i];
		IforkRootPath* new_path = new IforkRootPath(doms.size());
		new_path->set_path(path);
		precalculate_path(sol, new_path);

		vector<int> vals;
		new_path->get_applicable_vals(root_dom,vals);
		assert(0 < vals.size());
		root_paths_vals[vals[0]].push_back(new_path);
//		cout << "========================================================" <<  endl;
//		new_path->dump();
//		cout << "Is applicable in values " <<  vals[0];
//		cout << "--------------------------------------------------------" <<  endl;

		for (int j=1; j < vals.size(); j++) {
//			cout << " " << vals[j];
			IforkRootPath* cp_path = new IforkRootPath(new_path);
//			cp_path->dump();
			root_paths_vals[vals[j]].push_back(cp_path);
		}
//		cout << "--------------------------------------------------------" <<  endl;
//		cout << endl;

	}

	int num_created_paths = 0;
	for (int i = 0; i< root_dom; i++) {
		num_created_paths += root_paths_vals[i].size();
	}

	// Adding the empty path for the goal value only
	vector<Operator*> emp_path;
	IforkRootPath* empty_path = new IforkRootPath(doms.size());
	empty_path->set_path(emp_path);
	precalculate_path(sol, empty_path);

	root_paths_vals[root_goal].push_back(empty_path);

	// The values of each variable in support, initially all of them are needed.
	// After calculating the paths costs, we only need costs TO SOME of them - those that
	// appear in some support, for some path.
	to_keep.resize(doms.size());
	for (int i = 1; i < doms.size(); i++) {
		to_keep[i].assign(doms[i], -1);
	}

	int num_left_paths = 0;
//	cout << "The paths that are left" << endl;
	for (int i = 0; i< root_dom; i++) {
//		cout << "For root value " << i << " from " << root_paths_vals[i].size() << " only left" << endl;
		sort_and_remove_dominating_paths(i,root_paths_vals[i], remove_dominating);
		// Going over the paths that are left and picking up the needed supports
		num_left_paths += root_paths_values[i].size();
		for (int j = 0; j< root_paths_values[i].size(); j++) {

//			vector<pair<int,int> > first_needed;
//			root_paths_values[i][j]->get_first_needed_pairs(first_needed);
			const vector<pair<int,int> > &first_needed =
				root_paths_values[i][j]->get_first_needed_pairs();

			for (int k = 0; k < first_needed.size(); k++) {
				to_keep[first_needed[k].first][first_needed[k].second] = 0;
			}
//			root_paths_values[i][j]->dump();
		}
	}
	cout << "Total number of paths " << num_paths+1 << ", allocated " << num_created_paths+1 << ", left " << num_left_paths << endl;

	// Delete the array of lists
	delete [] root_paths_vals;
}



void BoundedIfork::sort_and_remove_dominating_paths(int root_val, list<IforkRootPath*>& paths, bool remove_dominating) {
	// Sorting paths by their costs increasingly and entering the result into vector member *root_paths_values*

//	cout << "Sorting and removing dominating paths for root value " << root_val << endl;
	for (int i = 0; i< root_paths_values[root_val].size(); i++) {
//		cout << i << endl;
		if (root_paths_values[root_val][i] != NULL) {
//			cout << i << endl;
//			cout << root_paths_values[root_val][i] << endl;
//			root_paths_values[root_val][i]->dump();
			delete root_paths_values[root_val][i];
//			cout << i << endl;
		}
	}

	root_paths_values[root_val].clear();
	if (0==paths.size())
		return;
	paths.sort(compare_IforkRootPath);

//	if (STATISTICS >= 2) {
//		cout << "Sorted list of paths for root value "<< root_val << " of size " << paths.size() << endl;
//	}
//	if (STATISTICS >= 3) {
//	for (list<IforkRootPath*>::iterator it=paths.begin(); it!=paths.end(); ++it)
//			(*it)->dump();
//		cout << "#######################################################################"<<endl;
//	}

	// Removing the dominating paths
	if (remove_dominating) {
		int sz = paths.size();
		list<IforkRootPath*>::iterator it=paths.end();
		for (int i = 0; i < sz ; i++) {
			// getting the last in the list
			it--;

			// Going over all other paths and checking if at least one of them is dominated
			// by the path in question. If so, erasing the path.
			for (list<IforkRootPath*>::iterator it2=paths.begin(); it2!=paths.end(); ++it2) {
				if (((*it) != (*it2)) && ((*it2)->is_dominated(*it))) {
//					if (STATISTICS >= 3) {
//						cout << "----->The path" << endl;
//						(*it)->dump();
//						cout << "----->dominates the path" << endl;
//						(*it2)->dump();
//						cout << "----->and won't be included" << endl;
//					}
					IforkRootPath* to_del = *it;
					paths.erase(it);
					delete to_del;
					break;
				}
			}
		}
	}

	// Taking the remaining paths
	for (list<IforkRootPath*>::iterator it=paths.begin(); it!=paths.end(); ++it) {
		root_paths_values[root_val].push_back(*it);
	}

//	if (STATISTICS >= 2) {
//		cout << "Sorted vector of paths for root value "<< root_val << " of size " << root_paths_values[root_val].size()  << endl;
//	}
//	if (STATISTICS >= 3) {
//		for (vector<IforkRootPath*>::iterator it=root_paths_values[root_val].begin();
//											it!=root_paths_values[root_val].end(); ++it)
//			(*it)->dump();
//		cout << "#######################################################################"<<endl;
//	}
}

void BoundedIfork::precalculate_path(double* sol, IforkRootPath* path) {

	const Problem* abs = get_mapping()->get_abstract();
	double ret = path->get_path_cost();

	int num_vars = abs->get_vars_number();
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
		ret += calculate_supp_cost(sol,v,supp);
	}
	path->set_first_needed_pairs();  // Finding the *supporting* parents
	path->set_needed_cost(ret);
//	path->clear_path_actions();
}

double BoundedIfork::calculate_supp_cost(double* sol, int v, vector<int>& supp) {
	double ret = 0.0;
	for (int i = 1; i < supp.size(); i++) {
		int d_ind = d_var(v,supp[i-1],supp[i]);
		ret += sol[d_ind];
	}
	return ret;
}

double BoundedIfork::get_solution_value(const State* state) {

	const State* abs_state = get_mapping()->get_abs_state(state);
	const state_var_t * eval_state = abs_state->get_buffer();
	int root_zero = (int) eval_state[0];

	double min_sol = DBL_MAX;
	int num_paths = root_paths_values[root_zero].size();

	// For each cycle free path:
	for (int p = 0; p < num_paths; p++) {
		IforkRootPath* path = root_paths_values[root_zero][p];
//		path->dump();
//		cout << "Dumping the first operator (orig):" << endl;
//		get_mapping()->get_orig_operator(path->get_first_operator())->dump();
		double sol = path->get_needed_cost();
		if (min_sol <= sol) { // already more or equal to the current minimum.
			continue;
		}

//		vector<pair<int,int> > first_needed;
//		path->get_first_needed_pairs(first_needed);
		const vector<pair<int,int> > &first_needed = path->get_first_needed_pairs();

		// Going over all *supporting* parents
		for (int i = 0; i < first_needed.size(); i++) {
			int from = (int) eval_state[first_needed[i].first];
			int to = first_needed[i].second;
			if (from != to) {
				sol += solution->get_value(d_var(first_needed[i].first,from,to));
			}
		}

		if (min_sol > sol) {
			min_sol = sol;
		}
		if (min_sol == 0)  //minimal possible - no need to continue.
			break;
	}
	return min_sol;
}

int BoundedIfork::d_var(int var, int val_0, int val_1) const {
	return (var-1)*max_domain*max_domain + val_0*max_domain + val_1;
//	cout << "x_" << ret << " = d(v_" << var << "," << val_0 << "," << val_1 << ")" << endl;
//	return ret;
}


int BoundedIfork::get_num_vars() const {
	return number_of_d_variables + number_of_h_variables + number_of_w_var_variables;

}
