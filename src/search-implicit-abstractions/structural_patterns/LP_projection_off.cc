#include "LP_projection_off.h"
#include "mapping.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "LP_heuristic.h"


LPProjection_OFF::LPProjection_OFF() :LPProjection() {
}

LPProjection_OFF::LPProjection_OFF(GeneralAbstraction* abs) :LPProjection(abs) {
}


LPProjection_OFF::LPProjection_OFF(vector<int>& pattern) :LPProjection(pattern) {
}



LPProjection_OFF::~LPProjection_OFF() {
}


void LPProjection_OFF::set_objective(){
	cout << "LPProjection_OFF::set_objective()" << endl;
	obj_func = new LPConstraint();

	//For each state
	// sum_{s\in S}  d(s)
	for (int d_ind = 0; d_ind < get_num_vars(); d_ind++) {
		obj_func->add_val(d_ind, 1.0);
	}
	obj_func->finalize();
}

/*
void LPProjection_OFF::set_static_constraints() {

	//static_constraints are
	// (I)   d(s') <= d(s") + w(a)   for all <s',a,s">
	// (II)    d(G) = 0              for all goals G

	const Problem* abs = get_mapping()->get_abstract();

	vector<vector<int> > states;
	abs->generate_state_transition_graph(states);
	const vector<Operator*> &ops = abs->get_operators();
	const vector<int> &doms = abs->get_variable_domains();

	// (I)   d(s') <= d(s") + w(a)   for all <s',a,s">
	for(int it = 0; it < ops.size(); it++) {
		if (ops[it]->is_redundant())
			continue;
		// Per action we generate all the states this action is applicable in.
		vector<int> generated = states[it];
		vector<int> free_vars;

		for(int i = 0; i < generated.size(); i++) {
			if (generated[i] < 0) {
				free_vars.push_back(i);
			}
		}
		add_distance_constraints(free_vars,generated,doms,ops[it]);
	}
	// (II)      d(G) = 0           for all goals G
	vector<int> goals;
	abs->get_goal_vals(goals);
	vector<int> free_vars;

	for(int i = 0; i < goals.size(); i++) {
		if (goals[i] < 0) {
			free_vars.push_back(i);
		}
	}
	add_goal_constraints(free_vars,goals,doms);
}
*/

void LPProjection_OFF::add_distance_constraints(vector<int> free_vars, vector<int> state, const vector<int>& doms, Operator* op) {

	if (free_vars.size() == 0) {
		// Stopping criteria
		vector<PrePost> pre = op->get_pre_post();
		// Creating the resulting state.
		vector<int> next_state = state;
		for (int i=0;i<pre.size();i++) {
			next_state[pre[i].var] = pre[i].post;
		}

		int d_ind0 = d_var(state);
		int d_ind1 = d_var(next_state);
		if (d_ind0==d_ind1)
			return;

		double c = op->get_double_cost();

		LPConstraint* lpc = new LPConstraint(-DBL_MAX,c,true);
		lpc->add_val(d_ind0, 1.0);
		lpc->add_val(d_ind1, -1.0);
		lpc->finalize();

		static_LPConstraints.push_back(lpc);
		return;
	}
	// Recursive step (for each value of one of the free variables
	int free_var = free_vars[free_vars.size()-1];
	free_vars.pop_back();
	int dom_size = doms[free_var];
	for(int i = 0; i < dom_size; i++) {
		state[free_var] = i;
		add_distance_constraints(free_vars,state,doms,op);
	}

}

void LPProjection_OFF::add_goal_constraints(vector<int> free_vars, vector<int> state, const vector<int>& doms) {

	if (free_vars.size() == 0) {
		// Stopping criteria

		int d_ind = d_var(state);
		static_LPConstraints.push_back(set_x_eq_0_constraint(d_ind, true));
		return;
	}
	// Recursive step (for each value of one of the free variables
	int free_var = free_vars[free_vars.size()-1];
	free_vars.pop_back();
	int dom_size = doms[free_var];
	for(int i = 0; i < dom_size; i++) {
		state[free_var] = i;
		add_goal_constraints(free_vars,state,doms);
	}
}
