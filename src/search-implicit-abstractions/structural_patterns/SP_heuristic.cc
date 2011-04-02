#include "SP_heuristic.h"
#include "SP_globals.h"
#include "var_projection.h"
#include <vector>
#include "../problem.h"
#include "../globals.h"
#include "../timer.h"
#include "general_abstraction.h"
#include "var_proj_mapping.h"
#include <iostream>
#include "projection_gen.h"
#include "binary_forks_gen.h"
#include "bounded_iforks_gen.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "../causal_graph.h"
#include <fstream>


SPHeuristic::SPHeuristic(bool use_cache)
    : Heuristic(use_cache) {
	original_problem = new Problem();
	SIZEOFPATTERNLIMIT = 0;
	PERCENTAGEOFENSEMBLE = 100;
	STATISTICS = 0;
	selected_ensemble = ALL_VARIABLES;
}

SPHeuristic::SPHeuristic(const Problem* prob, bool use_cache)
    : Heuristic(use_cache), original_problem(prob) {
	SIZEOFPATTERNLIMIT = 0;
	PERCENTAGEOFENSEMBLE = 100;
	STATISTICS = 0;
	selected_ensemble = ALL_VARIABLES;
}


SPHeuristic::~SPHeuristic() {

	for (int ind=0;ind<get_ensemble_size();ind++) {
		cout << "Deleting ensemble member " << ind << endl;
		delete get_ensemble_member(ind);
	}
	ensemble.clear();
}

void SPHeuristic::get_ensemble_values(const State& state, vector<double>& vals){

	assert(vals.size() == 0);
	vals.assign(get_ensemble_size(), 0.0);

	if (original_problem->is_goal(&state)) {
		return;
	}

	for (int ind=0;ind<get_ensemble_size();ind++) {
		vals[ind] = get_ensemble_member(ind)->get_solution_value(&state);
	}
	return;
}


int SPHeuristic::compute_heuristic(const State& state){
	if (original_problem->is_goal(&state)) {
		return 0;
	}
	double total = 0.0;
	for (int ind=0;ind<get_ensemble_size();ind++) {
		SolutionMethod* membr = get_ensemble_member(ind);
		if (!membr->is_active())
			continue;

		double sol = membr->get_solution_value(&state);
//		if (STATISTICS >= 3) {
//			cout << "Solution for " << ind << ": " << sol << endl;
//		}
		if (sol >= LP_INFINITY) {
			return DEAD_END;
		}
		total+=sol;
	}
//	if (STATISTICS >= 3) {
//		cout << "Total state evaluation " << total << endl;
//	}
	return ceil(total-0.0001);

}


void SPHeuristic::create_ensemble() {

	// Creating the ensemble by the given strategy
	if(strategy == FROM_FILE) {
		// Reading strategy file
	    ifstream input_file("output.strategy");
	    if ( input_file.is_open() ) {
	    	create_ensemble_from_file(input_file);
	    	return;
	    }
		cout << "No file is given. Filename should be: output.strategy" << endl;
		exit(1);
	}

//	if(strategy == FORKS_ONLY || strategy == FORKS_ONLY_LANDMARKS) {
	if(strategy == FORKS_ONLY) {
		if (selected_ensemble == MIXED_LANDMARK_FORKS_NON_LANDMARK_INVERTED_FORKS ||
				selected_ensemble == MIXED_NON_LANDMARK_FORKS_LANDMARK_INVERTED_FORKS) {
			cout << "Wrong variables strategy for forks only."<< endl;
			exit(1);
		}
		create_binary_forks();
		return;
	}
//	if(strategy == INVERTED_FORKS_ONLY || strategy == INVERTED_FORKS_ONLY_LANDMARKS) {
	if(strategy == INVERTED_FORKS_ONLY) {
		if (selected_ensemble == MIXED_LANDMARK_FORKS_NON_LANDMARK_INVERTED_FORKS ||
				selected_ensemble == MIXED_NON_LANDMARK_FORKS_LANDMARK_INVERTED_FORKS) {
			cout << "Wrong variables strategy for inverted forks only."<< endl;
			exit(1);
		}
		create_bounded_inverted_forks();
		return;
	}
//	if(strategy == BOTH_FORKS_AND_INVERTED_FORKS
//			|| strategy == BOTH_FORKS_AND_INVERTED_FORKS_LANDMARKS) {
	if(strategy == BOTH_FORKS_AND_INVERTED_FORKS) {
		create_binary_forks_and_bounded_iforks();
		return;
	}
	// Shouldn't happen
	cout << "NO STRATEGY SELECTED!!!" << endl;
	exit(1);
}

void SPHeuristic::create_ensemble_from_file(istream &//in
		) {
	cout << "Ensemble creation from file option is currently disabled." << endl;
	exit(1);
/*
	const vector<int> &var_dom = original_problem->get_variable_domains();
    int var_num = original_problem->get_vars_number();

    check_magic(in, "begin_strategy");
    int count;
    in >> count;
    if (count != var_num) {
    	cout << "The total number of variables does not match" << endl;
    	exit(1);
    }
    for(int v = 0; v < count; v++) {
		string name;
		in >> name;

		int var = original_problem->get_var_index(name);
		if (-1 == var) {
	    	cout << "The variable name " << name << " doesn't exist." << endl;
	    	exit(1);
	    }
		int var_strategy;  // 0 - nothing, 1 - fork only, 2 - inverted fork only, 3 - both
		in >> var_strategy;
		if (var_strategy < 0 || var_strategy > 3) {
			cout << "Unknown strategy for variable " << var << endl;
			exit(1);
		}
		if (var_strategy == 1 || (var_strategy == 3 && original_problem->has_goal_child(var))) {
			//creating fork for variable i
			create_binary_fork(var,var_dom[var], var_strategy == 1);
		}
		if (var_strategy == 2 || var_strategy == 3) {
			//creating inverted fork for variable i
			create_bounded_inverted_fork(var,var_dom[var]);
		}
	}
    check_magic(in, "end_strategy");
*/
}

bool SPHeuristic::is_heuristic_applicable() const {
	return original_problem->is_nonconditional();
}


///////////////////////////////////////////////////////////////////////////////
// There are multiple possible strategies for creating an ensemble.
// We are focusing on three primary possibilities - (i) creating forks only,
// (ii) creating inverted forks only, and (iii) creating both forks and inverted forks.
/* Old version (26/5/2010)
void SPHeuristic::create_binary_forks()
{
	// Creating the ensemble consisting of forks only (binary root domains)
	int var_count = original_problem->get_vars_number();
	const vector<int> &var_dom = original_problem->get_variable_domains();

	for (int v = 0; v < var_count; v++) {
		create_binary_fork(v,var_dom[v], true);
	}
}


void SPHeuristic::create_bounded_inverted_forks() {

	// Creating the ensemble - inverted forks (or singletons) are created for each
	// goal variable.
	int var_count = original_problem->get_vars_number();
	const vector<int> &var_dom = original_problem->get_variable_domains();

	for (int v = 0; v < var_count; v++) {
		create_bounded_inverted_fork(v,var_dom[v]);
	}
}



void SPHeuristic::create_binary_forks_and_bounded_iforks() {

	// Creating the ensemble
	int var_count = original_problem->get_vars_number();
	const vector<int> &var_dom = original_problem->get_variable_domains();

	for (int v = 0; v < var_count; v++) {
		if (original_problem->has_goal_child(v)) {
			create_binary_fork(v,var_dom[v], false);
		}
		create_bounded_inverted_fork(v,var_dom[v]);
	}
}




///////////////////////////////////////////////////////////////
void SPHeuristic::create_binary_fork(int v, int dom_size, bool create_singletones) {
	// Each variable is either a singleton or appears in some fork.
	// By default we use binarization "Leave One Out"

	vector<int> successors = original_problem->get_causal_graph()->get_successors(v);
//	vector<int> predecessors = original_problem->get_causal_graph()->get_predecessors(v);

	if (original_problem->has_goal_child(v)) {
		// Create fork (or PDB)
		if (SIZEOFPATTERNLIMIT > successors.size()) {
			vector<int> pattern = successors;
			pattern.insert(pattern.begin(),v);
			create_pattern(pattern);
			return;
		}
		// Size exceeds the limit
		create_binary_forkLOO(v, dom_size);
	}
	// No fork to create. If this is goal variable, and it doesn't appear
	// on any other fork (meaning if it has no parents), then singleton is created
	if (!create_singletones)
		return;

	if ((original_problem->is_goal_var(v))
//			&& (dom_size > 2) // Only if performing the domain abstraction
//			&& (0 == predecessors.size())
											) {  // The variable is singleton
		create_singleton(v);
	}
}


void SPHeuristic::create_bounded_inverted_fork(int v, int dom_size) {
// We use a ternarization by distance to goal.

//	vector<int> successors = original_problem->get_causal_graph()->get_successors(v);
	vector<int> predecessors = original_problem->get_causal_graph()->get_predecessors(v);

	if (original_problem->is_goal_var(v)) {
		if (0 < predecessors.size()) {
			// Create inverted fork (or PDB)
			if (SIZEOFPATTERNLIMIT > predecessors.size()) {
				vector<int> pattern = predecessors;
				pattern.insert(pattern.begin(),v);
				create_pattern(pattern);
			} else {
				create_bounded_inverted_forkDGV(v, 3, dom_size);

//				if (dom_size > 3) { // Only if performing the domain abstraction
					create_singleton(v);
//				}
			}
		} else {
			// This is a goal variable with no parents. Singleton is now created
			create_singleton(v);
		}
	}

}

void SPHeuristic::create_singleton(int var) {
	vector<int> pattern;
	pattern.push_back(var);
	create_pattern(pattern);
}


*/


// New version (26/5/2010)
void SPHeuristic::create_binary_forks()
{
	// Creating the ensemble consisting of forks only (binary root domains)
	int var_count = original_problem->get_vars_number();

	const vector<int> &var_dom = original_problem->get_variable_domains();
	const vector<string> &var_name = original_problem->get_variable_names();

	for (int v = 0; v < var_count; v++) {
		// Temporary hack - select only the landmark variables
//		if (strategy == FORKS_ONLY_LANDMARKS && var_name[v].find_first_of("-_") != string::npos)
//			continue;

		if (var_name[v].find_first_of("-_") != string::npos) {
			// landmark variable
			if (selected_ensemble == NON_LANDMARK_VARIABLES_ONLY)
				continue;
		} else {
			// non landmark variable
			if (selected_ensemble == LANDMARK_VARIABLES_ONLY)
				continue;
		}

		create_binary_fork(v,var_dom[v]);

		// Singletons
		vector<int> predecessors = original_problem->get_causal_graph()->get_predecessors(v);
		if (!original_problem->has_goal_child(v)) {
			if (0 < predecessors.size() && singletons_strategy == NECESSARY)
				continue;
			create_singleton(v);
		} else {
			if (0 == predecessors.size()) {
				// no pred, goal succ
				if (singletons_strategy == NECESSARY ||
						singletons_strategy == BY_DEFINITION)
					continue;
				if (var_dom[v] > 2)
					create_singleton(v);
			}
		}
	}
}


void SPHeuristic::create_bounded_inverted_forks() {

	// Creating the ensemble - inverted forks (or singletons) are created for each
	// goal variable.
	int var_count = original_problem->get_vars_number();

	const vector<int> &var_dom = original_problem->get_variable_domains();
	const vector<string> &var_name = original_problem->get_variable_names();

	for (int v = 0; v < var_count; v++) {
		// Temporary hack - select only the landmark variables
//		if (strategy == INVERTED_FORKS_ONLY_LANDMARKS
//				&& var_name[v].find_first_of("-_") == string::npos)
//			continue;


		if (var_name[v].find_first_of("-_") != string::npos) {
			// landmark variable
			if (selected_ensemble == NON_LANDMARK_VARIABLES_ONLY)
				continue;

		} else {
			// non landmark variable
			if (selected_ensemble == LANDMARK_VARIABLES_ONLY)
				continue;
		}

		create_bounded_inverted_fork(v,var_dom[v]);
		// Singletons
		vector<int> predecessors = original_problem->get_causal_graph()->get_predecessors(v);

		if (!original_problem->has_goal_child(v)) {
			if (0 == predecessors.size()) {
				// no pred, no goal succ
				create_singleton(v);
			} else {
				// pred, no goal succ
				if (singletons_strategy == NECESSARY ||
						singletons_strategy == BY_DEFINITION)
					continue;
				if (var_dom[v] > 2)
					create_singleton(v);
			}
		} else {
			if (0 == predecessors.size()) {
				// no pred, goal succ
				if (singletons_strategy == NECESSARY)
					continue;
				create_singleton(v);
			}
		}
	}
}


void SPHeuristic::create_binary_forks_and_bounded_iforks() {

	// Creating the ensemble
	int var_count = original_problem->get_vars_number();

//	vector<int> var_dom;
//	original_problem->get_variable_domains(var_dom);
	const vector<int> &var_dom = original_problem->get_variable_domains();
	const vector<string> &var_name = original_problem->get_variable_names();

	for (int v = 0; v < var_count; v++) {
//		if (strategy == BOTH_FORKS_AND_INVERTED_FORKS_LANDMARKS) {
//			if (var_name[v].find_first_of("-_") == string::npos) { // not landmark variable
//				create_binary_fork(v,var_dom[v]);
//				continue;
//			}
//			// landmark variable
//			create_bounded_inverted_fork(v,var_dom[v]);
//			continue;
//		}

		if (var_name[v].find_first_of("-_") != string::npos) {
			// landmark variable
			if (selected_ensemble == NON_LANDMARK_VARIABLES_ONLY)
				continue;

			if (selected_ensemble != MIXED_NON_LANDMARK_FORKS_LANDMARK_INVERTED_FORKS)
				create_binary_fork(v,var_dom[v]);
			if (selected_ensemble != MIXED_LANDMARK_FORKS_NON_LANDMARK_INVERTED_FORKS)
				create_bounded_inverted_fork(v,var_dom[v]);
		} else {
			// non landmark variable
			if (selected_ensemble == LANDMARK_VARIABLES_ONLY)
				continue;

			if (selected_ensemble != MIXED_LANDMARK_FORKS_NON_LANDMARK_INVERTED_FORKS)
				create_binary_fork(v,var_dom[v]);
			if (selected_ensemble != MIXED_NON_LANDMARK_FORKS_LANDMARK_INVERTED_FORKS)
				create_bounded_inverted_fork(v,var_dom[v]);
		}

		// Singletons
		vector<int> predecessors = original_problem->get_causal_graph()->get_predecessors(v);

		if (!original_problem->has_goal_child(v)) {
			if (0 < predecessors.size() && singletons_strategy == NECESSARY)
				continue;
			create_singleton(v);
		} else {
			if (0 == predecessors.size()) {
				// no pred, goal succ
				if (singletons_strategy == NECESSARY)
					continue;
				create_singleton(v);
			}
		}

	}
}



///////////////////////////////////////////////////////////////
void SPHeuristic::create_binary_fork(int v, int dom_size) {
	// By default we use binarization "Leave One Out"
	if (!original_problem->has_goal_child(v))
		return;

	vector<int> successors = original_problem->get_causal_graph()->get_successors(v);

	// Create fork (or PDB)
	if (SIZEOFPATTERNLIMIT > successors.size()) {
		vector<int> pattern = successors;
		pattern.insert(pattern.begin(),v);
		create_pattern(pattern);
		return;
	}
	// Size exceeds the limit
	create_binary_forkLOO(v, dom_size);
}


void SPHeuristic::create_bounded_inverted_fork(int v, int dom_size) {
// We use a ternarization by distance to goal.
	if (!original_problem->is_goal_var(v))
		return;

	vector<int> predecessors = original_problem->get_causal_graph()->get_predecessors(v);

	if (0 == predecessors.size())
		return;

	// Create inverted fork (or PDB)
	if (SIZEOFPATTERNLIMIT > predecessors.size()) {
		vector<int> pattern = predecessors;
		pattern.insert(pattern.begin(),v);
		create_pattern(pattern);
	} else {
		create_bounded_inverted_forkDGV(v, IFORKDOMBOUND, dom_size);
		return;
//		int var_num = original_problem->get_var_actions(v).size();
		// Bounding by |A_v|^{IFORKDOMBOUND - 1}
//		create_bounded_inverted_fork_check_paths(v, IFORKDOMBOUND, pow(var_num, IFORKDOMBOUND-1), dom_size);
		create_bounded_inverted_fork_check_paths(v, IFORKDOMBOUND, MAX_NUM_PATHS, dom_size);
	}
}

void SPHeuristic::create_singleton(int var) {
	if (!original_problem->is_goal_var(var))
		return;

	vector<int> pattern;
	pattern.push_back(var);
	create_pattern(pattern);
}



///////////////////////////////////////////////////////////////////////////////////
void SPHeuristic::create_binary_forkLOO(int v, int dom_size) {
	cout << "Fork for variable " << v;// << endl;

	// Creating Fork first
	ForksAbstraction* f = new ForksAbstraction(v);
	f->create(original_problem);

	cout << " over " << f->get_mapping()->get_abstract()->get_vars_number() << " variables." << endl;

	if (dom_size == 2) {
		// Setting the domain mapping to identity.
		Domain* abs_domain = create_LOO_domain(v,0,dom_size);
		// Creating the abstraction
		SolutionMethod* membr = add_binary_fork(f, abs_domain);
		add_ensemble_member(membr);
//		cout << "Adding member " << membr << endl;
		return;
	}
	// If the original domain is not binary.
	for (int val = 0; val < dom_size; val++) {
		Domain* abs_domain = create_LOO_domain(v,val,dom_size);
		// Creating the abstraction
//		add_ensemble_member(add_binary_fork(f, abs_domain));
		SolutionMethod* membr = add_binary_fork(f, abs_domain);
		add_ensemble_member(membr);
//		cout << "Adding member " << membr << endl;
	}
}


void SPHeuristic::create_bounded_inverted_forkDGV(int v, int bound, int dom_size) {
	cout << "Inverted Fork for variable " << v;// << endl;


	// Creating Inverted Fork first
	IforksAbstraction* ifork = new IforksAbstraction(v);
	ifork->create(original_problem);

	cout << " over " << ifork->get_mapping()->get_abstract()->get_vars_number() << " variables." << endl;
	cout << "Var: " << v << ", domain: " << dom_size << ", bound: " << bound << endl;

	if (dom_size <= bound) {
		// Setting the domain mapping to identity.
		Domain* abs_domain = create_id_domain(v,dom_size);
		// Creating the abstraction
		add_ensemble_member(add_bounded_inverted_fork(ifork, abs_domain));
		return;
	}
	// If the original domain is bigger than a given bound.
	vector<vector<int> > dom_vals;
	vector<int> distances;
	original_problem->get_domain_values_by_distance_to_goal(v,dom_vals,distances);

//	int has_dead_end = 0;
	int lb = 0, ub = 0;
	for (int i=0; i < distances.size();i++) {
//		if(-1 == distances[i])  {
//			has_dead_end = 1;
//			continue;
//		}
		if(ub < distances[i])  {
			ub = distances[i];
		}
	}
//	ub+= has_dead_end; // Adding one for dead end values

	while (ub > lb) {
		// Setting the domain mapping to distance from initial value.
		int upper = min(lb+bound-1,ub);
		cout << "Bounds [" <<lb << "," << upper << "]" << endl;
		Domain* abs_domain = create_DGV_domain(v,distances,lb,upper);

		lb += bound-1;
		// Creating the abstraction
		add_ensemble_member(add_bounded_inverted_fork(ifork, abs_domain));
	}
}

void SPHeuristic::create_inverted_fork_all_paths(int v, int dom_size) {
	cout << "Inverted Fork for variable " << v; // << " with no bounds" << endl;

	// Creating Inverted Fork first
	IforksAbstraction* ifork = new IforksAbstraction(v);
	ifork->create(original_problem);

	Problem* abs = ifork->get_mapping()->get_abstract();

	cout << " over " << abs->get_vars_number() << " variables, with no bounds." << endl;

	cout << "Total number of paths "
		 << abs->get_estimated_number_of_all_cycle_free_paths_to_goal(0)
		 << endl;
	// Setting the domain mapping to identity.
	Domain* abs_domain = create_id_domain(v,dom_size);
	// Creating the abstraction
	add_ensemble_member(add_bounded_inverted_fork(ifork, abs_domain));
}



void SPHeuristic::create_bounded_inverted_fork_check_paths(int v, int bound, int paths_bound, int dom_size) {
	cout << "Inverted Fork for variable " << v;// << endl;

	// Creating Inverted Fork first
	IforksAbstraction* ifork = new IforksAbstraction(v);
	ifork->create(original_problem);

	Problem* abs = ifork->get_mapping()->get_abstract();

	cout << " over " << abs->get_vars_number() << " variables." << endl;

	cout << "Var: " << v << ", domain: " << dom_size << ", bound: " << bound;


	if (dom_size <= bound) {
		cout << endl;
		// Setting the domain mapping to identity.
		Domain* abs_domain = create_id_domain(v,dom_size);
		// Creating the abstraction
		add_ensemble_member(add_bounded_inverted_fork(ifork, abs_domain));
		return;
	}

	if (abs->is_estimated_number_of_all_cycle_free_paths_to_goal_bounded(0,paths_bound)) {
		cout << ", paths: under " << paths_bound << endl;
		// Setting the domain mapping to identity.
		Domain* abs_domain = create_id_domain(v,dom_size);
		// Creating the abstraction
		add_ensemble_member(add_bounded_inverted_fork(ifork, abs_domain));
		return;
	}
	cout << endl << "Too many paths, domain decomposition is performed" << endl;

	// If the original domain is bigger than a given bound.
	vector<vector<int> > dom_vals;
	vector<int> distances;
	original_problem->get_domain_values_by_distance_to_goal(v,dom_vals,distances);

	int lb = 0, ub = 0;
	for (int i=0; i < distances.size();i++) {
		if(ub < distances[i])  {
			ub = distances[i];
		}
	}

	while (ub > lb) {
		// Setting the domain mapping to distance from initial value.
		int upper = min(lb+bound-1,ub);
		cout << "Bounds [" <<lb << "," << upper << "]" << endl;
		Domain* abs_domain = create_DGV_domain(v,distances,lb,upper);

		lb += bound-1;
		// Creating the abstraction
		add_ensemble_member(add_bounded_inverted_fork(ifork, abs_domain));
	}
}








void SPHeuristic::create_pattern(vector<int>& pattern) {
	// Creating the abstraction
	cout << "Pattern for variables ";
	for (int i=0;i<pattern.size();i++)
		cout <<"  " << pattern[i];
	cout << endl;
	add_ensemble_member(add_pattern(pattern));
}



void SPHeuristic::set_uniform_representatives_cost() {

	// Setting the cost of the representatives in each pattern
	// to be uniformly partitioned between ALL the representatives.
	const vector<Operator*> &ops = original_problem->get_operators();

	int num_ops = ops.size();
	for (int a_i = 0; a_i < num_ops; a_i++) {

		// Counting the number of actions
		vector<Operator*> abs_ops;
		for (int ind = 0; ind < get_ensemble_size(); ind++){
			SolutionMethod* membr = get_ensemble_member(ind);
			if (!membr->is_active())
				continue;

			membr->get_mapping()->get_abs_operators(ops[a_i],abs_ops);
		}
		int num_actions = abs_ops.size();
		if (num_actions > 0) {
			double abs_cost = ops[a_i]->get_double_cost() / num_actions;
			// Update costs
			for (int i=0;i<num_actions;i++) {
				abs_ops[i]->set_double_cost(abs_cost);
			}
		}
	}
}


void SPHeuristic::print_abstract_operators() {

	const vector<Operator*> &ops = original_problem->get_operators();

	int num_ops = ops.size();
	cout << "Printing operators and their abstract representatives" << endl;
	for (int a_i = 0; a_i < num_ops; a_i++) {
		ops[a_i]->dump();
		for (int ind = 0; ind < get_ensemble_size(); ind++){
			SolutionMethod* membr = get_ensemble_member(ind);
			if (!membr->is_active())
				continue;

			vector<Operator*> abs_ops;
			membr->get_mapping()->get_abs_operators(ops[a_i],abs_ops);

			int num_actions = abs_ops.size();
			for (int i=0;i<num_actions;i++) {
				cout << membr->get_abstraction_index() <<
				", " << membr->w_var(abs_ops[i]) << " (" <<
				membr->get_abstraction_index() + membr->w_var(abs_ops[i])
				        << "): ";
				abs_ops[i]->dump();
			}
		}
	}
}




Domain* SPHeuristic::create_LOO_domain(int var, int to_leave, int dom_size) const {

	Domain* abs_domain = new Domain(var,dom_size,2);
	for (int k =0; k < dom_size; k++) {
		if (to_leave == k) {
			abs_domain->set_value(k,0);
		} else {
			abs_domain->set_value(k,1);
		}
	}
	return abs_domain;
}



Domain* SPHeuristic::create_DGV_domain(int var, vector<int>& distances, int lb, int ub) const {

	int dom_size = distances.size();
	int new_size = ub - lb + 1;
	Domain* abs_domain = new Domain(var,dom_size,new_size);
	for (int k =0; k < distances.size(); k++) {
		// TODO: in general, distance < 0 should be removed from the problem
		if ((distances[k] > ub) || (distances[k] < 0)) {
			abs_domain->set_value(k,ub - lb);
			continue;
		}
		if (distances[k] < lb) {
			abs_domain->set_value(k,0);
			continue;
		}
		abs_domain->set_value(k,distances[k] - lb);
	}
//	abs_domain->dump();
	return abs_domain;
}


Domain* SPHeuristic::create_id_domain(int var, int dom_size) const {

	Domain* abs_domain = new Domain(var,dom_size,dom_size);
	for (int k =0; k < dom_size; k++) {
		abs_domain->set_value(k,k);
	}

	return abs_domain;
}




void SPHeuristic::initialize() {

	if (STATISTICS >= 1) {
		original_problem->dump();
	}
	if (0 == get_ensemble_size()) {
//        cout << "Creating ensemble " << g_timer << endl;

		create_ensemble();
//		cout << "Done Creating ensemble " << g_timer << endl;
		// print statistics
		cout << "SAS variables :: " << original_problem->get_vars_number() << endl;
		cout << "Ensemble size :: " << ensemble.size() << endl;
	}
	if (get_cost_partitioning_strategy() == UNIFORM) {
		// Setting the cost partitioning
		set_uniform_representatives_cost();
		//	set_smart_representatives_cost();
		//	set_smart_uniform_representatives_cost();
//		cout << "Done setting UNIFORM cost partitioning" << endl;
	}

	int ens_size = ensemble.size();
	int disk_size = 0;
	int tot_vars = 0;
	int ens_types[3] = {};
	for (int ind=0;ind<ens_size;ind++) {
		if (STATISTICS >= 1) {
			cout << "Ensemble member "<< ind << endl;
			ensemble[ind]->get_mapping()->get_abstract()->dump();
		}
		ensemble[ind]->initiate();

		if ((get_cost_partitioning_strategy() == INITIAL_OPTIMAL) ||
				(get_cost_partitioning_strategy() == GENERAL)) {
		//#ifdef USE_MOSEK
		#ifdef USE_LP
			ensemble[ind]->set_objective();
			ensemble[ind]->set_static_constraints();
		#else
				cout << "No LP Solver defined in this version" << endl;
				exit(1);
		#endif
		} else {
//			cout << "Solving ensemble member " << ind << " " << g_timer << endl;

//			cout << "Solving ensemble member " << ind << endl;
//			ensemble[ind]->get_mapping()->get_abstract()->dump();
			ensemble[ind]->solve();
//			cout << "Done Solving, removing abstract operators " << g_timer << endl;
			// The solution is currently exist, no need for the abstract actions.
			ensemble[ind]->remove_abstract_operators();  // Implemented only in the offline version
//			cout << "Done removing abstract operators " << g_timer << endl;
		}
		tot_vars += ensemble[ind]->get_num_vars();
		disk_size += ensemble[ind]->get_solution()->get_size();
		ens_types[ensemble[ind]->get_abstraction_type()]++;
	}

	cout << "*Forks* in Ensemble :: " << ens_types[0] << endl;
	cout << "*Inverted Forks* in Ensemble :: " << ens_types[1] << endl;
	cout << "*Projections* in Ensemble :: " << ens_types[2] << endl;

	// Activating by a given percentage
	deactivate_all();

    //srand(time(0));  // Initialize random number generator.
    // Selecting patterns from ensemble to participate in computing heuristic
    int counter = 0;
    while (counter == 0) {
    	for (int it = 0; it < get_ensemble_size(); it++) {
    		SolutionMethod* membr = get_ensemble_member(it);
   			int pstg = (rand() % 100) + 1;
   			if (pstg <= PERCENTAGEOFENSEMBLE) {
   				membr->set_abstraction_index(counter);
   				membr->activate();
   				counter += membr->get_num_vars();
    		}
    	}
    }

	if (STATISTICS >= 1) {
		cout << "The size of the SPDB (number of entries) is " << disk_size << " out of " << tot_vars << endl;
	}
}


//////////////////////////////////////////////////////////////////////////////////
void SPHeuristic::set_smart_representatives_cost() {

	// The costs are uniformly partitioned between the patterns, inside each pattern first the whole cost
	// is given to the root, then the minimum is found and the rest is partitioned uniformly between others.
	const vector<Operator*> &ops = original_problem->get_operators();

	int num_ops = ops.size();
	vector<double> pattern_costs;
	pattern_costs.assign(num_ops,0.0);
	for (int a_i = 0; a_i < num_ops; a_i++) {
		// Counting the number of actions
		vector<Operator*> abs_ops;
		int num_ptrns=0;
		for (int ind = 0; ind < get_ensemble_size(); ind++){
			SolutionMethod* membr = get_ensemble_member(ind);
			if (!membr->is_active())
				continue;

			int num_rep = membr->get_mapping()->get_abs_operators(ops[a_i],abs_ops);
			if (num_rep > 0)
				num_ptrns++;
		}
		if (num_ptrns > 0) {
			double abs_cost = ops[a_i]->get_double_cost() / num_ptrns;
			int act_ind = ops[a_i]->get_index();
			assert(act_ind<num_ops);
			pattern_costs[act_ind] = abs_cost;
		}
	}

	for (int ind = 0; ind < get_ensemble_size(); ind++){
		SolutionMethod* membr = get_ensemble_member(ind);
		if (!membr->is_active())
			continue;

		Mapping* map = membr->get_mapping();

		if (membr->get_abstraction_type() == FORK) {
			const vector<Operator*> &A_r = map->get_abstract()->get_var_actions(0);

			// Dividing root changing actions into two sets, by the post value
			double min0 = DBL_MAX;
			double min1 = DBL_MAX;

			for (int a = 0; a < A_r.size(); a++) {
				int act_ind = map->get_orig_operator(A_r[a])->get_index();
				double c = pattern_costs[act_ind];
				if (0 == A_r[a]->get_post_val(0)) {
					min0 = min(min0,c);
				} else {
					min1 = min(min1,c);
				}
			}
			// Set the costs of the actions in this pattern
			for (int a_i = 0; a_i < num_ops; a_i++) {
				// Counting the number of actions
				vector<Operator*> abs_ops;
				int num_rep = map->get_abs_operators(ops[a_i],abs_ops);
				if (num_rep == 0) {
					continue;
				}

				int root_ind = -1; // will hold the index of the root changing representative.
				for (int i=0;i<num_rep;i++) {
					if(-1 < abs_ops[i]->get_post_val(0)) {
						root_ind = i;
						break;  // There are no two representatives both changing the root of binary fork.
					}
				}

				int act_ind = ops[a_i]->get_index();
				double cost_to_share = pattern_costs[act_ind];

				if (-1 == root_ind) {
					//  All get the same cost
					for (int i=0;i<num_rep;i++) {
						abs_ops[i]->set_double_cost(cost_to_share / num_rep);
					}
				} else {
					// The root representative gets the minimum, all others get the rest
					if( 0 == abs_ops[root_ind]->get_post_val(0)) {
						abs_ops[root_ind]->set_double_cost(min0);
						cost_to_share -= min0;
					} else {
						abs_ops[root_ind]->set_double_cost(min1);
						cost_to_share -= min1;
					}
					for (int i=0;i<num_rep;i++) {
						if (i != root_ind) {
							abs_ops[i]->set_double_cost(cost_to_share / (num_rep-1));
						}
					}
				}
			}
			continue;
		}
		if (membr->get_abstraction_type() == INVERTED_FORK) {

			continue;
		}
		if (membr->get_abstraction_type() == PATTERN) {

			continue;
		}
	}
}



void SPHeuristic::set_smart_uniform_representatives_cost() {

	// The costs are uniformly partitioned between the patterns, inside each pattern first the whole cost
	// is given to the root, then the minimum is found and the rest is partitioned uniformly between others.
	const vector<Operator*> &ops = original_problem->get_operators();

	int num_ops = ops.size();
	vector<double> rep_costs;
	rep_costs.assign(num_ops,0.0);
	for (int a_i = 0; a_i < num_ops; a_i++) {
		// Counting the number of actions
		vector<Operator*> abs_ops;
		for (int ind = 0; ind < get_ensemble_size(); ind++){
			SolutionMethod* membr = get_ensemble_member(ind);
			if (!membr->is_active())
				continue;

			membr->get_mapping()->get_abs_operators(ops[a_i],abs_ops);
		}
		int num_rep = abs_ops.size();
		if (num_rep > 0) {
			double abs_cost = ops[a_i]->get_double_cost() / num_rep;
			int act_ind = ops[a_i]->get_index();
			assert(act_ind<num_ops);
			rep_costs[act_ind] = abs_cost;
		}
	}

	for (int ind = 0; ind < get_ensemble_size(); ind++){
		SolutionMethod* membr = get_ensemble_member(ind);
		if (!membr->is_active())
			continue;

		Mapping* map = membr->get_mapping();

		if (membr->get_abstraction_type() == FORK) {
			const vector<Operator*> &A_r = map->get_abstract()->get_var_actions(0);

			// Dividing root changing actions into two sets, by the post value
			double min0 = DBL_MAX;
			double min1 = DBL_MAX;

			for (int a = 0; a < A_r.size(); a++) {
				int act_ind = map->get_orig_operator(A_r[a])->get_index();
				double c = rep_costs[act_ind];
				if (0 == A_r[a]->get_post_val(0)) {
					min0 = min(min0,c);
				} else {
					min1 = min(min1,c);
				}
			}
			// Set the costs of the actions in this pattern
			for (int a_i = 0; a_i < num_ops; a_i++) {
				// Counting the number of actions
				vector<Operator*> abs_ops;
				int num_rep = map->get_abs_operators(ops[a_i],abs_ops);
				if (num_rep == 0) {
					continue;
				}

				int root_ind = -1; // will hold the index of the root changing representative.
				for (int i=0;i<num_rep;i++) {
					if(-1 < abs_ops[i]->get_post_val(0)) {
						root_ind = i;
						break;  // There are no two representatives both changing the root of binary fork.
					}
				}

				int act_ind = ops[a_i]->get_index();
				double cost_to_share = rep_costs[act_ind] * num_rep;

				if (-1 == root_ind) {
					//  All get the same cost
					for (int i=0;i<num_rep;i++) {
						abs_ops[i]->set_double_cost(cost_to_share / num_rep);
					}
				} else {
					// The root representative gets the minimum, all others get the rest
					if( 0 == abs_ops[root_ind]->get_post_val(0)) {
						abs_ops[root_ind]->set_double_cost(min0);
						cost_to_share -= min0;
					} else {
						abs_ops[root_ind]->set_double_cost(min1);
						cost_to_share -= min1;
					}
					for (int i=0;i<num_rep;i++) {
						if (i != root_ind) {
							abs_ops[i]->set_double_cost(cost_to_share / (num_rep-1));
						}
					}
				}
			}
			continue;
		}
		if (membr->get_abstraction_type() == INVERTED_FORK) {

			continue;
		}
		if (membr->get_abstraction_type() == PATTERN) {

			continue;
		}
	}
}


void SPHeuristic::deactivate_all() {
	for (int ind = 0; ind < get_ensemble_size(); ind++){
		get_ensemble_member(ind)->deactivate();
	}
}

int SPHeuristic::get_num_vars() {
	int res = 0;
	for (int ind = 0; ind < get_ensemble_size(); ind++){
		res += get_ensemble_member(ind)->get_num_vars();
	}
	return res;
}

int SPHeuristic::get_num_active_vars() {
	int res = 0;
	for (int ind = 0; ind < get_ensemble_size(); ind++){
		if (get_ensemble_member(ind)->is_active())
			res += get_ensemble_member(ind)->get_num_vars();
	}
	return res;
}



////////////////////////////////////////////////////////////////////////////////////////////////////
// Moving Offline to the parent class

SolutionMethod* SPHeuristic::add_binary_fork(GeneralAbstraction* abs) {
//	return new BinaryForks_OFF(abs);
	return new BinaryFork(abs);
}

SolutionMethod* SPHeuristic::add_bounded_inverted_fork(GeneralAbstraction* abs) {
	return new BoundedIfork(abs);
}

SolutionMethod* SPHeuristic::add_pattern(GeneralAbstraction* abs) {
	return new Projection(abs);
}


/////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////
// Creating multiple domain abstraction using the same base abstraction
SolutionMethod* SPHeuristic::add_binary_fork(ForksAbstraction* fork, Domain* abs_domain) {
//	return new BinaryForks_OFF(fork, abs_domain);
	return new BinaryFork(fork, abs_domain);
}

SolutionMethod* SPHeuristic::add_bounded_inverted_fork(IforksAbstraction* ifork, Domain* abs_domain) {
	return new BoundedIfork(ifork, abs_domain);
}

/////////////////////////////////////////////////////////////////////////////////

/*
SolutionMethod* SPHeuristic::add_binary_fork(Domain* abs_domain) {
//	BinaryForks_OFF* bf = new BinaryForks_OFF();
	BinaryFork* bf = new BinaryFork();
	bf->set_root_var_and_domain(abs_domain);
	bf->create(original_problem);
	bf->set_abstraction_type(FORK);
	return bf;
}

SolutionMethod* SPHeuristic::add_bounded_inverted_fork(Domain* abs_domain) {
//	BoundedIforks_OFF* bif = new BoundedIforks_OFF();
	BoundedIfork* bif = new BoundedIfork();
	bif->set_root_var_and_domain(abs_domain);
	bif->create(original_problem);
	bif->set_abstraction_type(INVERTED_FORK);
	return bif;
}
*/
SolutionMethod* SPHeuristic::add_pattern(vector<int>& pattern) {
//	Projection_OFF* ptrn = new Projection_OFF(pattern);
	Projection* ptrn = new Projection(pattern);
	ptrn->create(original_problem);
	ptrn->set_abstraction_type(PATTERN);
	return ptrn;
}


void SPHeuristic::solve_all() {
	for (int ind = 0; ind < get_ensemble_size(); ind++){
		get_ensemble_member(ind)->solve();
	}
}

void SPHeuristic::solve_all_and_remove_operators() {
	for (int ind = 0; ind < get_ensemble_size(); ind++){
//		cout << "Solving " << ind << endl;
		get_ensemble_member(ind)->solve();
//		cout << "Removing operators" << endl;
		get_ensemble_member(ind)->remove_abstract_operators();  // Implemented only in the offline version
//		cout << "Done Removing operators" << endl;
	}
}

void SPHeuristic::check_cost_partition() {

	// Checking the cost of the actions
	// to be correctly partitioned between the representatives.
	const vector<Operator*> &ops = original_problem->get_operators();

	int num_ops = ops.size();
	for (int a_i = 0; a_i < num_ops; a_i++) {

		// Counting the number of actions
		vector<vector<Operator*> > abs_ops;
		double tot_cost = 0.0;
		int num_abs = 0;
		for (int ind = 0; ind < get_ensemble_size(); ind++){
			SolutionMethod* membr = get_ensemble_member(ind);
			if (!membr->is_active())
				continue;

			vector<Operator*> abs_operators;
			num_abs += membr->get_mapping()->get_abs_operators(ops[a_i],abs_operators);
//			cout << "Inc num abs operators for ensemble " << ind << " is " << num_abs << endl;
			abs_ops.push_back(abs_operators);
			for (int i=0;i<abs_operators.size();i++) {
				tot_cost += abs_operators[i]->get_double_cost();
			}
		}
		double orig_cost = ops[a_i]->get_double_cost();
		if (tot_cost > orig_cost + 0.0000001) {
			cout << "Problem with cost partition of the operator"<< endl;
			ops[a_i]->dump();
			cout << "Into "<< num_abs << " representatives"<< endl;
			for (int ind = 0; ind < get_ensemble_size(); ind++){
				SolutionMethod* membr = get_ensemble_member(ind);
				if (!membr->is_active())
					continue;

				for (int i=0;i<abs_ops[ind].size();i++) {
					cout << membr->get_abstraction_index() <<
					", " << membr->w_var(abs_ops[ind][i]) << " (" <<
					membr->get_abstraction_index() + membr->w_var(abs_ops[ind][i])
					        << "): ";
					abs_ops[ind][i]->dump();
				}
			}
		}
	}
}
