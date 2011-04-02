#include "lm_enriched_paths_heuristic.h"
#include "globals.h"
#include "operator.h"
#include "successor_generator.h"
#include "lm_graph_paths.h"

#include <sstream>
#include <math.h>


LmEnrichedPathsHeuristic::LmEnrichedPathsHeuristic(
		LandmarksGraph& l, const char *arg, bool use_cache) :
	LmEnrichedHeuristic(l, arg, use_cache) {

}

LmEnrichedPathsHeuristic::LmEnrichedPathsHeuristic(
		const Problem* prob, LandmarksGraph& l, const char *arg, bool use_cache) :
	LmEnrichedHeuristic(prob, l, arg, use_cache) {
}

LmEnrichedPathsHeuristic::~LmEnrichedPathsHeuristic() {

}

void LmEnrichedPathsHeuristic::set_needed_landmarks() {
//	create_paths_all_paths();

//	create_paths_covering();

	create_paths_no_orderings();
}

// Setting a variable for each landmark, no orderings.
void LmEnrichedPathsHeuristic::create_paths_no_orderings() {

	cout << "Setting variable for each path." << endl;
	assert(en_vars.size() == 0);

	vector<LandmarkNode*> to_remove;
	// Loop on all landmarks, select goal landmarks to start from
	for (set<LandmarkNode*>::const_iterator it = lgraph.get_nodes().begin(); it
			!= lgraph.get_nodes().end(); it++) {
		LandmarkNode& curr_land = **it;

		if (!curr_land.is_goal()) {
			vector<LandmarkNode*> path;
			path.push_back(*it);
			en_vars.push_back(path);
		} else {
			to_remove.push_back(*it);
		}
	}
	for(int i=0; i < to_remove.size(); i++) {
		lgraph.rm_landmark_node(to_remove[i]);
	}

}


// Setting a variable for path, greedily finding paths covering the links of landmarks graph
void LmEnrichedPathsHeuristic::create_paths_covering() {
// Building a graph using landmark ids, and keeping a hash-map of LandmarkNodes

	cout << "Setting variable for each path." << endl;
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
void LmEnrichedPathsHeuristic::create_paths_all_paths() {

	cout << "Setting variable for each path." << endl;
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
void LmEnrichedPathsHeuristic::build_enriched_variables(
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

State* LmEnrichedPathsHeuristic::build_enriched_initial() {

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

void LmEnrichedPathsHeuristic::update_enriched_state(const State& state) {

	int orig_vars_num = original_problem->get_vars_number();

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

void LmEnrichedPathsHeuristic::build_enriched_goal(vector<pair<int, int> >& en_goal) {

	original_problem->get_goal(en_goal);
	// The first value, representing the goal landmark is always the goal value for these variables.
	int orig_vars_num = original_problem->get_vars_number();
	for (int i = 0; i < en_vars.size(); i++) {
		en_goal.push_back(make_pair(orig_vars_num+i, 0));
	}
}


// TODO: rewrite for this class
void LmEnrichedPathsHeuristic::build_enriched_prepost(const Operator* op, vector<PrePost>& pre) {

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

bool LmEnrichedPathsHeuristic::is_subpath(vector<LandmarkNode*>& path_a, vector<LandmarkNode*>& path_b) {
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

void LmEnrichedPathsHeuristic::expand_path(vector<LandmarkNode*>& path, vector<vector<LandmarkNode*> >& paths) {
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
