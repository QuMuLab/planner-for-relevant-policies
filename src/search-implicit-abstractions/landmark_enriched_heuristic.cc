#include "landmark_enriched_heuristic.h"
#include "globals.h"
#include "operator.h"
#include "successor_generator.h"
#include "structural_patterns/SP_globals.h"

#include <sstream>
#include <math.h>
#include <vector>


LandmarkEnrichedHeuristic::LandmarkEnrichedHeuristic(
		LandmarksGraph& l,	const char *arg, bool use_cache)
	: Heuristic(use_cache), lgraph(l), lm_status_manager(lgraph), h_arg(arg) {
	original_problem = new Problem();
}

LandmarkEnrichedHeuristic::LandmarkEnrichedHeuristic(
		const Problem* prob, LandmarksGraph& l, const char *arg, bool use_cache)
	: Heuristic(use_cache), lgraph(l), lm_status_manager(lgraph), original_problem(prob), h_arg(arg) {
}

LandmarkEnrichedHeuristic::~LandmarkEnrichedHeuristic() {
	if (original_problem)
		delete original_problem;  // Either created here, or just before a call to constructor.
	delete en_state_vars;
	delete en_state;
	delete en_prob;
	delete h;
}


// Setting a variable for each landmark, no orderings.
void LandmarkEnrichedHeuristic::create_paths_no_orderings(bool init_landmarks) {

	cout << "Setting variable for each landmark." << endl;
	assert(en_vars.size() == 0);

	vector<LandmarkNode*> to_remove;
	// Loop on all landmarks, select goal landmarks to start from
	for (set<LandmarkNode*>::const_iterator it = lgraph.get_nodes().begin(); it
			!= lgraph.get_nodes().end(); it++) {
		LandmarkNode& curr_land = **it;

		if (!curr_land.is_goal() &&
			(init_landmarks || !curr_land.is_true_in_state(*(original_problem->get_initial_state())))) {
			vector<LandmarkNode*> path;
			path.push_back(*it);
			en_vars.push_back(path);
//		} else {
//			to_remove.push_back(*it);
		}
	}
	for(int i=0; i < to_remove.size(); i++) {
		lgraph.rm_landmark_node(to_remove[i]);
	}

}


// Setting a variable for path, greedily finding paths covering the links of landmarks graph
void LandmarkEnrichedHeuristic::create_paths_covering() {
// Building a graph using landmark ids, and keeping a hash-map of LandmarkNodes

	cout << "Setting variable for each path - link covering." << endl;
	assert(en_vars.size() == 0);
	LmGraphPaths lgpaths(lgraph);
	// Until no uncovered edges left, getting the longest path, marking the covered edges
	while (!lgpaths.is_edgeless()) {
		vector<LandmarkNode*> path;
		lgpaths.extract_longest_path(path);
		en_vars.push_back(path);
	}
	// Creating 1-node paths for singletons
	vector<LandmarkNode*> &singletons = lgpaths.get_singleton_nodes();
	for (int i = 0; i < singletons.size(); i++) {
		vector<LandmarkNode*> path;
		path.push_back(singletons[i]);
		en_vars.push_back(path);
	}
	/*
	for (int i = 0; i < en_vars.size(); i++) {
		cout << "Path " << i << endl;
		for (int lm = 0; lm < en_vars[i].size(); lm++) {
			cout << "  " << en_vars[i][lm]->id;
		}
		cout << endl;
	}
	*/
}

////////////////////////////////////////////////////////////////////////////////////////////////
// Sets a variable for each possible path in landmarks graph
void LandmarkEnrichedHeuristic::create_paths_all_paths() {

	cout << "Setting variable for each path - all paths." << endl;
	assert(en_vars.size() == 0);

	// Loop on all landmarks, select goal landmarks to start from
	for (set<LandmarkNode*>::const_iterator it = lgraph.get_nodes().begin(); it
			!= lgraph.get_nodes().end(); it++) {
		LandmarkNode& curr_land = **it;

		if (curr_land.is_goal()) {
			vector<LandmarkNode*> path;
			path.push_back(*it);
			expand_path(path,en_vars);
		}
	}
	// Going over the found paths and checking if some of them are subpaths of others
	vector<int> to_remove;
	to_remove.assign(en_vars.size(),0);

	for (int i = 0; i < en_vars.size(); i++) {
		for (int j = 0; j < en_vars.size(); j++) {
			if (i==j)
				continue;
			if (is_subpath(en_vars[i],en_vars[j])) {
				to_remove[i] = 1;
				break;
			}
		}
	}

	int sz= en_vars.size();
	for (int i = sz;i>0; i--) {
		if (to_remove[i]>0)
			en_vars.erase(en_vars.begin()+i);
	}
}

////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////
void LandmarkEnrichedHeuristic::build_enriched_variables(
		vector<string> &en_variable_name, vector<int> &en_variable_domain) {
	// Initial original variables
	int orig_vars_num = original_problem->get_vars_number();

	for (int i = 0; i < orig_vars_num; i++) {
		en_variable_name.push_back(original_problem->get_variable_name(i));
		en_variable_domain.push_back(original_problem->get_variable_domain(i));
	}

	for (int i = 0; i < en_vars.size(); i++) {
		string nm;

		for (int lm = en_vars[i].size(); lm > 0; lm--) {
			if (lm < en_vars[i].size())
				nm += "___";

			LandmarkNode& curr_land = *en_vars[i][lm-1];

			for (int j = 0; j < curr_land.vars.size(); j++) {

				// Convert int to string
				stringstream land_val;
				land_val << curr_land.vals[j];
				if (j > 0)
					nm += "_";

				nm+= original_problem->get_variable_name(curr_land.vars[j]) + "->" + land_val.str();
			}
		}
		// The name is constructed along the path and the domain is the path plus initial value (the last)
		en_variable_name.push_back(nm);
		en_variable_domain.push_back(en_vars[i].size()+1);
	}
}

State* LandmarkEnrichedHeuristic::build_enriched_initial() {

	int orig_vars_num = original_problem->get_vars_number();
	const state_var_t* orig_init_buff = original_problem->get_initial_state()->get_buffer();
	state_var_t* init_buff = new state_var_t[orig_vars_num + en_vars.size()];

	for (int i = 0; i < orig_vars_num; i++) {
		init_buff[i] = orig_init_buff[i];
	}

	for (int i = 0; i < en_vars.size(); i++, orig_vars_num++) {
		// Going over the landmarks on the path and setting the last (first) reached (or the last value)
		init_buff[orig_vars_num] = en_vars[i].size();

		for (int lm = 0; lm < en_vars[i].size(); lm++) {

			if (en_vars[i][lm]->status == lm_reached) {
				init_buff[orig_vars_num] = lm;
				break;
			}
		}
	}
	return new State(init_buff);
}

void LandmarkEnrichedHeuristic::update_enriched_state(const State& state) {

//	int orig_vars_num = original_problem->get_vars_number();
	int orig_vars_num = en_prob->get_vars_number() - en_vars.size();

	for (int i = 0; i < orig_vars_num; i++) {
		en_state_vars[i] = state.get_buffer()[i];
	}

	for (int i = 0; i < en_vars.size(); i++, orig_vars_num++) {
		// Going over the landmarks on the path and setting the last (first) reached (or the last value)
		en_state_vars[orig_vars_num] = en_vars[i].size();

		for (int lm = 0; lm < en_vars[i].size(); lm++) {

			if (en_vars[i][lm]->status == lm_reached) {
				en_state_vars[orig_vars_num] = lm;
				break;
			}
		}
	}
}

void LandmarkEnrichedHeuristic::build_enriched_goal(vector<pair<int, int> >& en_goal) {

	original_problem->get_goal(en_goal);
	// The first value, representing the goal landmark is always the goal value for these variables.
	int orig_vars_num = original_problem->get_vars_number();
	for (int i = 0; i < en_vars.size(); i++) {
		en_goal.push_back(make_pair(orig_vars_num+i, 0));
	}
}

void LandmarkEnrichedHeuristic::build_enriched_prepost(const Operator* op, vector<PrePost>& pre) {

	pre = op->get_pre_post();
	int pre_sz = pre.size();

	int orig_vars_num = original_problem->get_vars_number();

	for (int i = 0; i < en_vars.size(); i++) {
		// Check if this variable should be added to the action effects
		// If so, adding an effect for each achieving effect
		int new_var = orig_vars_num + i;

		for (int j = 0; j < pre_sz; j++) {
			// Check if this effect achieves some landmark on the path
			for (int lm = 0; lm < en_vars[i].size(); lm++) {
				LandmarkNode& curr_land = *en_vars[i][lm];
				// Going over the disjunction of facts and adding an effect, if needed (once)
				for (int v = 0; v < curr_land.vars.size(); v++) {
					if ((pre[j].var == curr_land.vars[v])
							&& (pre[j].post == curr_land.vals[v])) {
						vector<Prevail> cond = pre[j].cond;
						cond.push_back(Prevail(new_var, lm+1));
						pre.push_back(PrePost(new_var, -1, lm, cond));
						break;
					}
				}
			}
		}
	}
}



////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////

bool LandmarkEnrichedHeuristic::is_subpath(vector<LandmarkNode*>& path_a, vector<LandmarkNode*>& path_b) {
	// Returns true if path_a is subpath of path_b
	if (path_a.size() > path_b.size())
		return false;
	int ptr_b = 0;
	for (int i=0; i<path_a.size(); i++) {
		while ((ptr_b < path_b.size()) && (path_a[i]->id != path_b[ptr_b]->id)) {
			ptr_b++;
		}
		if (ptr_b == path_b.size())
			return false;
		ptr_b++;
	}
	return true;
}

void LandmarkEnrichedHeuristic::expand_path(vector<LandmarkNode*>& path, vector<vector<LandmarkNode*> >& paths) {
//	if (path.size() == 1)
//		cout << "Expanding path from node " << path[0]->id << endl;

	LandmarkNode* last = path[path.size()-1];
	bool has_parents = false;
    for (hash_map<LandmarkNode*, edge_type, hash_pointer>::const_iterator
            parent_it = last->parents.begin(); parent_it
            != last->parents.end(); parent_it++) {
    	has_parents = true;
        LandmarkNode* parent_p = parent_it->first;
        vector<LandmarkNode*> new_path = path;
        new_path.push_back(parent_p);
        vector<vector<LandmarkNode*> > new_paths;
        expand_path(new_path,new_paths);
        for (int i=0; i < new_paths.size();i++)
        	paths.push_back(new_paths[i]);
    }
    if (!has_parents) {
    	paths.push_back(path);
    }
}


////////////////////////////////////////////////////////////////////////////////////////





void LandmarkEnrichedHeuristic::create_remove_landmarks_operators(vector<Operator*> &en_operators) {

	// Build an action for each landmark variable from 1 to 0 - to prevent non
	// reachable states in the abstractions.
	int orig_vars_num = original_problem->get_vars_number();
	for (int i = 0; i < en_vars.size(); i++, orig_vars_num++) {
		// Going over the variables and create an action for each possible value reduction

		vector<Prevail> no_cond, no_prevail;
		for (int lm = 0; lm < en_vars[i].size(); lm++) {

			vector<PrePost> new_pre;
			new_pre.push_back(PrePost(orig_vars_num,lm,lm+1, no_cond));

			string action_name;
#ifdef DEBUGMODE
			// Convert int to string
			stringstream var_ind_name;
			var_ind_name << orig_vars_num << ":" << lm;
			action_name = "reduce landmark value " + var_ind_name.str();
#endif
			Operator* en_op = new Operator(false, no_prevail, new_pre, action_name, 1.0);
			en_op->set_index(en_operators.size());
			en_operators.push_back(en_op);
		}
	}
}

int LandmarkEnrichedHeuristic::compute_heuristic(const State& state) {
	// Get landmarks that have been true at some point (put into
	// "reached_lms") and their cost

//	if (original_problem->is_goal(&state))
//		return 0;

	if (lm_status_manager.update_lm_status(state))
		return DEAD_END;


	// Get enriched state from state
	update_enriched_state(state);
	h->evaluate(*en_state);
	if (h->is_dead_end())
		return DEAD_END;
	return h->get_heuristic();
}

void LandmarkEnrichedHeuristic::initialize() {

	if (original_problem == NULL)
		original_problem = new Problem();
	// Setting the paths that correspond to variables of the enriched task
	if(VARIABLESTYPE == VARIABLE_PER_LANDMARK) {
		create_paths_no_orderings(true);
	} else if(VARIABLESTYPE == VARIABLE_PER_LANDMARK_NO_INIT) {
		create_paths_no_orderings(false);
	} else if (VARIABLESTYPE == ALL_LANDMARK_PATHS_VARIABLES) {
		create_paths_all_paths();
	} else if (VARIABLESTYPE == LANDMARK_PATHS_COVERING_VARIABLES) {
		create_paths_covering();
	} else {
		cout << "Unknown type" << endl;
		exit(1);
	}

	lm_status_manager.set_landmarks_for_initial_state(*original_problem->get_initial_state());
	lm_status_manager.update_lm_status(*original_problem->get_initial_state());
	const char *c = h_arg;
//	h_arg++;

	// Create the enriched problem and the heuristic
	if (c[0] == 'a') {
		cout << "Not implemented in this version." << endl;
		exit(1);
		bool del_unreached = true;
		for(int i=1; c[i] != 0; i++) {
			if (c[i] == 'U')
				del_unreached = false;
		}
		en_prob = build_enriched_problem(true, del_unreached);
		h = build_fd_heuristic(h_arg+1, en_prob);
	} else if (c[0] == 's'){
		en_prob = build_enriched_problem(false, false);
		h = build_sp_heuristic(h_arg+1, en_prob);
		// Remove unnecessary constructs from en_prob and the whole original problem - not needed
		if (original_problem)
			delete original_problem;
		original_problem = NULL;
		h->evaluate(*(en_prob->get_initial_state()));
		en_prob->delete_causal_graph();
		en_prob->delete_DTGs();
		en_prob->delete_operators();

	} else {
		cout << "Unknown option: " << c[0] << " for enriched heuristic." << endl;
		exit(1);
	}
//	en_prob->write_everything();

}

Problem* LandmarkEnrichedHeuristic::build_enriched_problem(bool is_HHH,
		bool create_additional_operators) {

	//Build enriched variables
	vector<string> en_variable_name;
	vector<int> en_variable_domain;
	build_enriched_variables(en_variable_name, en_variable_domain);

	// Build enriched operators
	vector<Operator*> en_operators;
	build_enriched_operators(en_operators, create_additional_operators);

	// Build enriched axioms
	vector<Operator> axioms;
	build_enriched_axioms(axioms);

//	int en_vars_size = en_variable_domain.size();
	// Build enriched initial state
	State *en_initial_state = build_enriched_initial();

	// Build enriched goal
	vector<pair<int, int> > en_goal;
	build_enriched_goal(en_goal);

	Problem* prob = new Problem(en_variable_name, en_variable_domain,
			en_initial_state, en_goal, en_operators, axioms, is_HHH);

	// Build DTGs
	vector<DomainTransitionGraph*> dtgs;
	original_problem->get_DTGs(dtgs);

	int orig_vars_num = original_problem->get_vars_number();

	//Step 1: Add DTGs for the original variables
	for(int i=orig_vars_num; i < en_variable_domain.size(); i++) {
        DomainTransitionGraph *dtg = new DomainTransitionGraph(i, en_variable_domain[i]);
        dtgs.push_back(dtg);
	}
	prob->set_DTGs(dtgs);

	//Step 2: Add DTGs manually for the new variables. This is necessary only if the
	//        new variables have more then 2 domain values (not a binary domain).
	for(int i=orig_vars_num; i < en_variable_domain.size(); i++) {
		prob->fill_DTG(i);
	}
//	lgraph.dump_dot();
//	prob->dump();
	// Create en_state
	en_state_vars = new state_var_t[prob->get_vars_number()];
	en_state = new State(en_state_vars);

	return prob;
}

void LandmarkEnrichedHeuristic::build_enriched_operators(vector<Operator*> &en_operators,
		bool create_additional_operators) {
//TODO: FIND BUG that appears on instance p04 of transport-strips-ipc6 domain.
	assert(en_operators.size() == 0);

	const vector<Operator*> ops = original_problem->get_operators();
	for (int i = 0; i < ops.size(); i++){
		en_operators.push_back(build_enriched_operator(ops[i]));
	}
	if (create_additional_operators)
		create_remove_landmarks_operators(en_operators);

}

Operator* LandmarkEnrichedHeuristic::build_enriched_operator(const Operator* op) {

	vector<PrePost> pre;
	build_enriched_prepost(op,pre);

	Operator* new_op = new Operator(op->is_axiom(), op->get_prevail(), pre, op->get_name(), op->get_double_cost());
	new_op->set_index(op->get_index());
	return new_op;
}

void LandmarkEnrichedHeuristic::build_enriched_axioms(vector<Operator> &en_operators) {

	vector<Operator> axi = original_problem->get_axioms();

	for (int i = 0; i < axi.size(); i++) {
		Operator* a = build_enriched_operator(&axi[i]);
		en_operators.push_back(*a);
	}
}


bool LandmarkEnrichedHeuristic::reach_state(const State& parent_state,
		const Operator &op, const State& state) {
    lm_status_manager.update_reached_lms(parent_state, op, state);
	return true;
}

void LandmarkEnrichedHeuristic::reset() {
	lm_status_manager.clear_reached();
	lm_status_manager.set_landmarks_for_initial_state(*g_initial_state);
}
/*
void LandmarkEnrichedHeuristic::print_statistics() const {
	h->print_statistics();
}
*/

