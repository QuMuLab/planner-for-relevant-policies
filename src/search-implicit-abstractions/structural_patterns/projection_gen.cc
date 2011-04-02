#include "projection_gen.h"
#include "mapping.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "LP_heuristic.h"
#include "SP_globals.h"

Projection::Projection() {
	abstraction = new VariablesProjection();
}

Projection::Projection(GeneralAbstraction* abs) {
	abstraction = abs;
}


Projection::Projection(vector<int>& pattern) {
	abstraction = new VariablesProjection(pattern);
//	set_pattern(pattern);
}

Projection::~Projection() {
	// TODO Auto-generated destructor stub
}


void Projection::initiate() {

	const Problem* abs = get_mapping()->get_abstract();
	const vector<int> &doms = abs->get_variable_domains();
	num_vars = abs->get_vars_number();

	int num_states = 1;
	for(int i=0;i<doms.size();i++) {
		multiplier.push_back(num_states);
		num_states *= doms[i];
	}
	set_solution(new Solution());

	number_of_d_variables = num_states;
	number_of_h_variables = 1;
	number_of_w_var_variables = 0;

}


void Projection::solve() {

	//static_constraints are
	// (I)   d(s') <= d(s") + w(a)   for all <s',a,s">
	// (II)    d(G) = 0              for all goals G

	Mapping* map = get_mapping();
	const Problem* abs = map->get_abstract();

	vector<vector<int> > states;
	abs->generate_state_transition_graph(states);
	const vector<Operator*> &ops = abs->get_operators();
	const vector<int> &doms = abs->get_variable_domains();

	int numLPvars = get_num_vars() + 1;
	double** sol = new double*[numLPvars];

	for (int i=0;i<numLPvars;i++) {
		sol[i] = new double[numLPvars];
		for (int j=0;j<numLPvars;j++) {
			if (i==j)
				sol[i][j] = 0.0;
			else
				sol[i][j] = LP_INFINITY;
		}
	}

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
		set_distances(sol,free_vars,generated,doms,ops[it]);
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
	set_goal_distances(sol,free_vars,goals,doms,numLPvars-1);

	for (int k=0;k<numLPvars;k++) {
		for (int i=0;i<numLPvars;i++) {
			for (int j=0;j<numLPvars;j++) {
				sol[i][j] = min(sol[i][j],sol[i][k] + sol[k][j]);
			}
		}
	}

	solution->clear_solution();

	for (int k=0;k<numLPvars-1;k++) {
		solution->set_value(k,sol[k][numLPvars-1]);
	}

	for (int i=0;i<numLPvars;i++) {
		delete [] sol[i];
	}
	delete [] sol;

}

double Projection::get_solution_value(const State* state) {

	const State* abs_state = get_mapping()->get_abs_state(state);
	return solution->get_value(d_var(abs_state));
}

void Projection::set_distances(double **sol, vector<int> free_vars, vector<int> state, const vector<int>& doms, Operator* op) {

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
		sol[d_ind0][d_ind1] = min(sol[d_ind0][d_ind1],c);
		return;
	}
	// Recursive step (for each value of one of the free variables
	int free_var = free_vars[free_vars.size()-1];
	free_vars.pop_back();
	int dom_size = doms[free_var];
	for(int i = 0; i < dom_size; i++) {
		state[free_var] = i;
		set_distances(sol,free_vars,state,doms,op);
	}

}

void Projection::set_goal_distances(double **sol, vector<int> free_vars, vector<int> state, const vector<int>& doms, int last) {

	if (free_vars.size() == 0) {
		// Stopping criteria
		int d_ind = d_var(state);
		sol[d_ind][last] = 0;
		return;
	}
	// Recursive step (for each value of one of the free variables
	int free_var = free_vars[free_vars.size()-1];
	free_vars.pop_back();
	int dom_size = doms[free_var];
	for(int i = 0; i < dom_size; i++) {
		state[free_var] = i;
		set_goal_distances(sol,free_vars,state,doms,last);
	}
}


int Projection::d_var(const State* state) const {

	int ret = 0;
	for (int i = 0; i < num_vars; i++) {
		int s = (int) (*state)[i];
		int m = multiplier[i];
		ret += s*m;
//		cout << " " << s;
	}
//	cout << " = x_" << ret << endl;
	return ret;
}



int Projection::d_var(vector<int>& state) const {
	int ret = 0;
	for (int i = 0; i < state.size(); i++) {
		ret += state[i]*multiplier[i];
//		cout << " " << state[i];
	}
//	cout << " = x_" << ret << endl;
	return ret;
}


int Projection::get_num_vars() const {
	return number_of_d_variables + number_of_h_variables + number_of_w_var_variables;
}

