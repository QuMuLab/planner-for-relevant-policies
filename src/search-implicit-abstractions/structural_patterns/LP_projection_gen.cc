#include "LP_projection_gen.h"
#include "mapping.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "LP_heuristic.h"

LPProjection::LPProjection() :Projection() {
}

LPProjection::LPProjection(GeneralAbstraction* abs) :Projection(abs) {
}


LPProjection::LPProjection(vector<int>& pattern) :Projection(pattern) {
}


LPProjection::~LPProjection() {
}
/*
void LPProjection::solve() {
	set_objective();
	set_static_constraints();
}
*/

void LPProjection::initiate() {
	Projection::initiate();
	const Problem* abs = get_mapping()->get_abstract();
	number_of_w_var_variables = abs->get_actions_number();
}


void LPProjection::set_static_constraints() {

	//static_constraints are
	// (I)   d(s') <= d(s") + w(a)   for all <s",a,s'>
	// (II)      h <= d(G)           for all goals G

	const Problem* abs = get_mapping()->get_abstract();

	vector<vector<int> > states;
	abs->generate_state_transition_graph(states);
	const vector<Operator*> &ops = abs->get_operators();
	const vector<int> &doms = abs->get_variable_domains();

	// (I)   d(s') <= d(s") + w(a)   for all <s",a,s'>
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
	// (II)      h <= d(G)           for all goals G
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

void LPProjection::get_dynamic_constraints(const State* state, vector<LPConstraint*> &dyn_constr) {

	// The only dynamic constraint is d(s_I) = 0
	int d_ind = d_var(get_mapping()->get_abs_state(state));
	dyn_constr.push_back(set_x_eq_0_constraint(d_ind, false));
}

void LPProjection::add_distance_constraints(vector<int> free_vars, vector<int> state, const vector<int>& doms, Operator* op) {

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

		int w_ind = w_var(op);
		static_LPConstraints.push_back(set_x_leq_y_plus_z_constraint(d_ind1, d_ind0, w_ind, true));
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

void LPProjection::add_goal_constraints(vector<int> free_vars, vector<int> state, const vector<int>& doms) {

	if (free_vars.size() == 0) {
		// Stopping criteria

		int d_ind = d_var(state);
		int h_ind = h_var();
		static_LPConstraints.push_back(set_x_leq_y_constraint(h_ind, d_ind, true));
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

int LPProjection::h_var() const {
	return number_of_d_variables;
}

int LPProjection::w_var(Operator* a) const {
	const Problem* abs = get_mapping()->get_abstract();
	int ret =  number_of_d_variables + number_of_h_variables + abs->get_action_index(a);
//	cout << "x_" << ret << " = w_a, a:";
//	a->dump();
	return ret;
}

//int LPProjection::num_w_var_vars() const {
//	return get_mapping()->get_abstract()->get_actions_number();
//}


