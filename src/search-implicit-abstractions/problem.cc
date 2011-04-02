#include "problem.h"
#include "operator.h"
#include "state.h"
#include <vector>
#include <math.h>
#include <fstream>

using namespace std;

Problem::Problem(bool translator_cg) {

	vector<Operator*> ops;
	int num_ops = g_operators.size();
/*
	for (int i = 0; i < num_ops; i++) {
		ops.push_back(&g_operators[i]);
	}
*/
	for (int i = 0; i < num_ops; i++) {
		ops.push_back(new Operator(g_operators[i]));
	}

	create_problem(g_variable_name, g_variable_domain,
			g_initial_state, g_goal, ops, g_axioms);

//	set_causal_graph(g_causal_graph);
	int num_vars = g_variable_name.size();
	set_causal_graph(new CausalGraph(num_vars, ops, translator_cg)); // different Causal graph definition
	set_DTGs(g_transition_graphs);
}

Problem::Problem(vector<string> var_name,
				 vector<int> var_domain,
				 const State* init_state,
				 vector<pair<int, int> > g,
				 vector<Operator*> ops, vector<Operator> axi,
				 bool is_HHH) {

	create_problem(var_name, var_domain, init_state, g, ops, axi);
	set_causal_graph(new CausalGraph(variable_name.size(),operators, is_HHH));
	//set_DTGs(g_transition_graphs);
	// Does not create DTGs --- no need.
}

/* No Problem Copy Constructor currently present - need to implement Causal Graph Copy Constructor first.
Problem::Problem(const Problem& p) {
	is_cond = p.is_nonconditional();
	variable_name = p.get_variable_names();
	variable_domain = p.get_variable_domains();
	initial_state = new State(*(p.get_initial_state()));
	p.get_goal(goal);
	vector<Operator*> ops = p.get_operators();
	for (int i=0; i < ops.size();i++) {
		operators.push_back(new Operator(*(ops[i])));
	}
	cg = new CausalGraph(*(p.get_causal_graph()));
	p.get_DTGs(dtgs); 								// No Copying DTGs allowed.
	get_goal_vals(goal_vars);
	int num_vars = variable_name.size();
	v_operators.resize(num_vars);
	for(int it = 0; it < operators.size(); it++){
		const vector<PrePost> pre = operators[it]->get_pre_post();
		for(int it2 = 0; it2 < pre.size(); it2++) {
			int ind = pre[it2].var;
			assert(ind >= 0 && ind < num_vars);
			vector<Operator*> op;
			if (0 < v_operators[ind].size()) {
				op = v_operators[ind];
			}
			op.push_back(operators[it]);
			v_operators[ind] = op;
		}
	}
	axioms = p.get_axioms();
}
*/

Problem::~Problem() {
	delete_causal_graph();
	delete_operators();
	delete_DTGs();
}

void Problem::create_problem(vector<string>& var_name,
				 vector<int>& var_domain,
				 const State* init_state,
				 vector<pair<int, int> >& g,
				 vector<Operator*>& ops,
				 vector<Operator>& axi) {

	variable_name = var_name;
	variable_domain = var_domain;
	initial_state = init_state;
	goal = g;
//	int num_ops = ops.size();
	int num_vars = var_name.size();
	v_operators.resize(num_vars);
	axioms = axi;

	// Adding index to the operator - by its position
	for (int i =0;i<ops.size();i++) {
		ops[i]->set_index(i);
		operators.push_back(ops[i]);
	}

	goal_vars.assign(num_vars,-1);
	for(int i = 0; i < goal.size(); i++)
		goal_vars[goal[i].first] = goal[i].second;

	// Partitioning operators by modified variables for quicker access.
	for(int it = 0; it < operators.size(); it++){
		const vector<PrePost> pre = operators[it]->get_pre_post();
		for(int it2 = 0; it2 < pre.size(); it2++) {
			int ind = pre[it2].var;
			assert(ind < num_vars);
			assert(ind >= 0);
			if (pre[it2].pre == pre[it2].post) {
				cout << "====> Check operator prepost condition " << endl;
				operators[it]->dump();
			}
			vector<Operator*> op;
			if (0 < v_operators[ind].size()) {
				op = v_operators[ind];
			}
			op.push_back(operators[it]);
			v_operators[ind] = op;
		}
	}

	is_cond = set_nonconditional();

}

/* Not used anymore
void Problem::make_SAS_operators(Operator* op, vector<Operator*>& ops) {

	int ind = -1;
	const vector<PrePost> pre = op->get_pre_post();
	int pre_size = pre.size();
	for (int i = 0; i < pre_size; i++) {
		if (pre[i].pre == -1)
			ind = i;
	}

	if (-1 == ind) {
		ops.push_back(op);
		return;
	}

//	vector<PrePost> pre = op->get_pre_post();
	vector<Prevail> prv = op->get_prevail();
	vector<PrePost> pre2;
	for (int i=0; i < pre_size; i++) {
		if (i != ind) {
			pre2.push_back(pre[i]);
		}
	}

	int var = pre[ind].var;
	int post = pre[ind].post;
	int dom_size= variable_domain[var];
	for (int val=0;val< dom_size; val++) {
		vector<PrePost> new_pre = pre2;
		vector<Prevail> new_prv = prv;

		if (post == val) {
			if (0==new_pre.size())
				continue;
			new_prv.push_back(Prevail(var,val));
		} else {
			new_pre.push_back(PrePost(var,val,post,pre[ind].cond));
		}
		string nm;
#ifdef DEBUGMODE

		nm = op->get_name();
		const int max_str_len(42);
		char my_string[max_str_len+1];
		snprintf(my_string, max_str_len, ":%d:%d:",var,val);
		nm += my_string;
#endif

		Operator* new_op = new Operator(false,new_prv,new_pre,nm,op->get_cost());

		make_SAS_operators(new_op, ops);
	}
}
*/

bool Problem::is_goal(const State* state) const {

	for(int i = 0; i < goal.size(); i++){

		int val = (*state)[goal[i].first];
		if(val != goal[i].second)
			return false;
	}

	return true;
}


void Problem::generate_state_transition_graph(vector<vector<int> >& states) const {
	// The vector that is returned is of length equal to number of actions.
	// Each entry i consist of vector of integers, representing a set of states
	// in which action i is applicable.

	const vector<Operator*> &ops = get_operators();
	for(int it = 0; it < ops.size(); it++) {
		// Per action we generate all the states this action is applicable in.
		vector<int> generated;
		get_applicable_states(ops[it],generated);
		states.push_back(generated);
	}
}

void Problem::get_applicable_states(Operator* op, vector<int>& vals) const {

	vector<Prevail> prv = op->get_prevail();
	vector<PrePost> pre = op->get_pre_post();

	int num_vars = variable_domain.size();

	vals.assign(num_vars,-1);

	for (int i=0;i<prv.size();i++) {
		vals[prv[i].var] = prv[i].prev;
	}

	for (int i=0;i<pre.size();i++) {
		vals[pre[i].var] = pre[i].pre;
	}

}

/*
 * Not used

set<const State*> Problem::get_successors(const State* state) const {
	// This method creates new states that are not deleted here.
	vector<Operator*> ops = get_applicable_actions(state);
	set<const State*> succ;

	for(int it = 0; it < ops.size(); it++)
		succ.insert(new State(*state,*(ops[it])));

	return succ;
}

vector<Operator*> Problem::get_applicable_actions(const State* state) const{
	// The complexity of this method doesn't allow to apply it too much.
	vector<Operator*> succ;

	for(int it = 0; it < operators.size(); it++)
		if (operators[it]->is_applicable(*state))
			succ.push_back(operators[it]);

	return succ;
}
*/


void Problem::fill_DTG(int ) {
// TODO: Filling the DTG for variable var manually

}


void Problem::get_domain_decomposition_by_distance(int v, int val, vector<vector<int> >& vals, vector<int>& len_from_val) const {
	// Distance from initial state.
	vector<int> first, open;
	const vector<int> &doms = get_variable_domains();
	int dom_size = doms[v];

	len_from_val.assign(dom_size,-1);
	len_from_val[val] = 0;
	int counted = 1;

	first.push_back(val);
	dtgs[v]->get_successors(val,open);
	vals.push_back(first);
	vals.push_back(open);
	for (int i=0; i < open.size();i++) {
		len_from_val[open[i]] = 1;
		counted++;
	}

	// Open keeps the front (all values of distance k)
	while ((counted < dom_size) && (open.size() > 0)) {
		// The open list for next iteration
		vector<int> next;
		for (int i=0; i < open.size();i++) {
			// For each value of distance k we develop all its successors
			// If those successors were not developed sooner, then they are
			// of distance k+1
			vector<int> new_open;
			dtgs[v]->get_successors(open[i],new_open);
			for (int j=0; j < new_open.size();j++) {
				if (-1 == len_from_val[new_open[j]]) {
					// Updating the distance
					len_from_val[new_open[j]] = len_from_val[open[i]] + 1;
					next.push_back(new_open[j]);
					counted++;
				}
			}
		}
		vals.push_back(next);
		open = next;
	}

}

void Problem::get_domain_values_by_distance_to_goal(int v, vector<vector<int> >& vals, vector<int>& len_to_goal) const {

	int g_v = get_goal_val(v);
	vector<int> first, open;
	const vector<int> &doms = get_variable_domains();
	int dom_size = doms[v];

	len_to_goal.assign(dom_size,-1);
	len_to_goal[g_v] = 0;
	int counted = 1;

//	vector<int> pred[dom_size];
	vector<vector<int> > pred;
	pred.resize(dom_size);
	for (int i=0;i<dom_size;i++) {
		vector<int> succ;
		dtgs[v]->get_successors(i,succ);

		for (int j=0;j<succ.size();j++){
			pred[succ[j]].push_back(i);
		}
	}


	first.push_back(g_v);

	open = pred[g_v];
	vals.push_back(first);
	vals.push_back(open);

	for (int i=0; i < open.size();i++) {
		if (-1 == len_to_goal[open[i]]) {
			len_to_goal[open[i]] = 1;
			counted++;
		}
	}

	// Open keeps the front (all values of distance k)
	while ((counted < dom_size) && (open.size() > 0)) {
		// The open list for next iteration
		vector<int> next;
		for (int i=0; i < open.size();i++) {
			// For each value of distance k we develop all its successors
			// If those successors were not developed sooner, then they are
			// of distance k+1
			vector<int> new_open = pred[open[i]];
			for (int j=0; j < new_open.size();j++) {
				if (-1 == len_to_goal[new_open[j]]) {
					// Updating the distance
					len_to_goal[new_open[j]] = len_to_goal[open[i]] + 1;
					next.push_back(new_open[j]);
					counted++;
				}
			}
		}
		vals.push_back(next);
		open = next;
	}
}


void Problem::get_cycle_free_paths_by_length(int v, int length, vector<vector<Operator*> >& paths) const {

	// Returns all the paths to goal (if defined) of length <= the given bound
	if (length > 2){
		cout << "The greatest implemented bound is 2" << endl;    // To be implemented in the future
		exit(1);
	}
	int g_v = get_goal_val(v);
	if (-1==g_v) return;     // No goal

//	vector<Operator*> A_v;
//	get_var_actions(v,A_v);
	const vector<Operator*> &A_v = get_var_actions(v);


	// Getting the paths of length 1.
	for (int a=0;a<A_v.size(); a++) {
		if (g_v == A_v[a]->get_post_val(v)) {
			vector<Operator*> ops;
			ops.push_back(A_v[a]);
			paths.push_back(ops);
		}
	}
	if (length == 1) return;

	// This is for the ternary case only, general algorithm will be implemented in the future
	int sz = paths.size();
	for (int i=0; i < sz; i++) {
		// Going over the paths of length 1
		vector<Operator*> ops = paths[i];
		int new_g = ops[0]->get_pre_val(v);
		if (-1 == new_g) {
			// We don't need to extend this path further.
			continue;
		}
		for (int a=0;a<A_v.size(); a++) {
			if (new_g == A_v[a]->get_post_val(v)) {
				// Checking for loops - in general case cycle free paths.
				if (g_v != A_v[a]->get_pre_val(v)) {
					vector<Operator*> new_ops;
					new_ops.push_back(A_v[a]); // In general case - insert new operator first
					new_ops.push_back(ops[0]);
					paths.push_back(new_ops);
				}
			}
		}
	}
}


/////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////
// Returns all cycle free paths from any value to the goal
void Problem::get_all_cycle_free_paths_to_goal(int v, vector<vector<Operator*> >& paths) const {

	int g_v = get_goal_val(v);
	if (-1==g_v) return;     // No goal

	const vector<Operator*> &A_v = get_var_actions(v);
	if (0 == paths.size()) {
		// Getting the paths of length 1 - to start with.
		for (int a=0;a<A_v.size(); a++) {
			if (g_v == A_v[a]->get_post_val(v)) {
				vector<Operator*> ops;
				ops.push_back(A_v[a]);
				paths.push_back(ops);
			}
		}

	}

	for (int i=0; i < paths.size(); i++) {
		// Going over all the paths found so far and trying to expand each one
		vector<Operator*> ops = paths[i];
		if (variable_domain[v] - 1 == ops.size()) {
			// We don't need to extend this path further.
			continue;
		}

		int new_g = ops[0]->get_pre_val(v);
		if (-1 == new_g) {
			// We don't need to extend this path further.
			continue;
		}
		for (int a=0;a<A_v.size(); a++) {
			if (new_g != A_v[a]->get_post_val(v))
				continue;

			// Checking for loops - in general case cycle free paths.
			int new_pre = A_v[a]->get_pre_val(v);
			if (-1 != new_pre) {
				// Going over the path, checking if the new value is not an effect of any action
				bool is_loop = false;
				for (int j=0; j < ops.size(); j++) {
					if (new_pre == ops[j]->get_post_val(v)) {
						is_loop = true;
						break;
					}
				}
				if (is_loop)
					continue;

				// Build a new path and try to extend it
				vector<Operator*> new_path = ops;
				new_path.insert(new_path.begin(), A_v[a]);
				vector<vector<Operator*> > new_paths;
				new_paths.push_back(new_path);
				get_all_cycle_free_paths_to_goal(v, new_paths);

				// Add the new paths to the previously found
				for (int p=0; p < new_paths.size(); p++) {
					paths.push_back(new_paths[p]);
				}
			} else {
				// Add the -1 ending path to the previously found
				vector<Operator*> new_path = ops;
				new_path.insert(new_path.begin(), A_v[a]);
				paths.push_back(new_path);
			}
		}
	}
}



/////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////
// Returns the number of all cycle free paths from any value to the goal
int Problem::get_estimated_number_of_all_cycle_free_paths_to_goal(int v) const {
	// Estimation Algorithm from
	// B. Roberts and D. P. Kroese, Estimating the Number of s-t Paths in a Graph, Journal of Graph Algorithms and Applications, vol. 11, no. 1, pp. 195–214 (2007)
	int g_v = get_goal_val(v);
	if (-1==g_v) return 0;     // No goal

	const vector<Operator*> &A_v = get_var_actions(v);

	int dom = get_variable_domain(v);

	int** A = new int *[dom];
	for( int i = 0 ; i < dom ; i++ )
		A[i] = new int [dom];

	for( int i = 0 ; i < dom ; i++ )
		for( int j = 0 ; j < dom ; j++ )
			A[i][j] = 0;

	// Building the adjacent matrix
	for (int a=0;a<A_v.size(); a++) {
		int pre = A_v[a]->get_pre_val(v);
		int post = A_v[a]->get_post_val(v);

		int start_val = (-1 == pre) ? 0 : pre;
		int end_val = (-1 == pre) ? dom : pre;

		for (int val=start_val;val<=end_val;val++) {
			if (val != post) {
				A[val][post] ++;
			}
		}
	}

	for( int i = 0 ; i < dom ; i++ ) {
		for( int j = 0 ; j < dom ; j++ )
			cout << A[i][j] << " " ;

		cout << endl;
	}

	int num_paths = 0;
	int N = 100;
	for( int i = 0 ; i < dom ; i++ ) {
		// For each value in the domain, except the goal, estimate the number of paths to the goal
		if (i == g_v)
			continue;
		// Building an adjacent matrix for i - removing links to i
		vector<vector<int> > adj;
		adj.resize(dom);

		for( int j = 0 ; j < dom ; j++ ) {
			for( int k = 0 ; k < dom ; k++ ) {
				if (k == i)
					continue;
				if (A[j][k] > 0)
					adj[j].push_back(k);
			}
		}

		// Running N times, counting the total value.
		// Estimated number of paths from i is num_paths/N
		for (int step = 0; step < N; step++) {
			vector<vector<int> > new_adj = adj;
			int curr = i;
			int val = 1;
			while (curr != g_v) {
				int num_ch = new_adj[curr].size();
				if (num_ch == 0) {
					val = 0;
					break;
				}
				int tmp_val = 1;
				for( int ch = 0 ; ch < num_ch ; ch++ ) {
					int to = new_adj[curr][ch];
					tmp_val = tmp_val*A[curr][to];
				}
				val = val*tmp_val;
				int next = rand() % num_ch;
				curr = new_adj[curr][next];
				// Update adjacent matrix - remove links to new current
				for( int j = 0 ; j < dom ; j++ ) {
					for( int k = 0 ; k < new_adj[j].size() ; k++ ) {
						if (new_adj[j][k] == curr) {
							new_adj[j].erase(new_adj[j].begin()+k);
							break;
						}
					}
				}
			}
			num_paths += val;
		}
	}

	for( int i = 0 ; i < dom ; i++ )
		delete [] A[i];

	delete [] A;

	return ceil(num_paths/N);
}

// Returns true if the number of all cycle free paths from any value to the goal is under the given bound
bool Problem::is_estimated_number_of_all_cycle_free_paths_to_goal_bounded(int v, int bound) const {
	// Estimation Algorithm from
	// B. Roberts and D. P. Kroese, Estimating the Number of s-t Paths in a Graph, Journal of Graph Algorithms and Applications, vol. 11, no. 1, pp. 195–214 (2007)
	int g_v = get_goal_val(v);
	if (-1==g_v) return 0;     // No goal

	const vector<Operator*> &A_v = get_var_actions(v);

	int dom = get_variable_domain(v);

	int** A = new int *[dom];
	for( int i = 0 ; i < dom ; i++ )
		A[i] = new int [dom];

	for( int i = 0 ; i < dom ; i++ )
		for( int j = 0 ; j < dom ; j++ )
			A[i][j] = 0;

	// Building the adjacent matrix
	for (int a=0;a<A_v.size(); a++) {
		int pre = A_v[a]->get_pre_val(v);
		int post = A_v[a]->get_post_val(v);

		int start_val = (-1 == pre) ? 0 : pre;
		int end_val = (-1 == pre) ? dom : pre;

		for (int val=start_val;val<=end_val;val++) {
			if (val != post) {
				A[val][post] ++;
			}
		}
	}

	for( int i = 0 ; i < dom ; i++ ) {
		for( int j = 0 ; j < dom ; j++ )
			cout << A[i][j] << " " ;

		cout << endl;
	}

	bool is_bounded = true;
	int num_paths = 0;
	int N = 100;
	for( int i = 0 ; i < dom ; i++ ) {
		// For each value in the domain, except the goal, estimate the number of paths to the goal
		if (i == g_v)
			continue;
		// Building an adjacent matrix for i - removing links to i
		vector<vector<int> > adj;
		adj.resize(dom);

		for( int j = 0 ; j < dom ; j++ ) {
			for( int k = 0 ; k < dom ; k++ ) {
				if (k == i)
					continue;
				if (A[j][k] > 0)
					adj[j].push_back(k);
			}
		}

		// Running N times, counting the total value.
		// Estimated number of paths from i is num_paths/N
		for (int step = 0; step < N; step++) {
			vector<vector<int> > new_adj = adj;
			int curr = i;
			int val = 1;
			while (curr != g_v) {
				int num_ch = new_adj[curr].size();
				if (num_ch == 0) {
					val = 0;
					break;
				}
				int tmp_val = 1;
				for( int ch = 0 ; ch < num_ch ; ch++ ) {
					int to = new_adj[curr][ch];
					tmp_val = tmp_val*A[curr][to];
				}
				val = val*tmp_val;
				int next = rand() % num_ch;
				curr = new_adj[curr][next];
				// Update adjacent matrix - remove links to new current
				for( int j = 0 ; j < dom ; j++ ) {
					for( int k = 0 ; k < new_adj[j].size() ; k++ ) {
						if (new_adj[j][k] == curr) {
							new_adj[j].erase(new_adj[j].begin()+k);
							break;
						}
					}
				}
			}
			num_paths += val;
		}
		if (num_paths/N > bound) {
			is_bounded = false;
			break;
		}
	}

	for( int i = 0 ; i < dom ; i++ )
		delete [] A[i];

	delete [] A;

	return is_bounded;
}





void Problem::set_operators_to_uniform_cost() {
	for (int a=0;a<operators.size(); a++) {
		operators[a]->set_double_cost(1.0);
	}
}


void Problem::increase_operators_cost() {
	for (int a=0;a<operators.size(); a++) {
		operators[a]->set_double_cost(operators[a]->get_double_cost() + 1.0);
	}
}


bool Problem::set_nonconditional() {

	for(int it = 0; it < operators.size(); it++){
		vector<PrePost> pre = operators[it]->get_pre_post();
		for(int it2 = 0; it2 < pre.size(); it2++)
			if (pre[it2].cond.size() > 0) return false;
	}
	return true;
}


bool Problem::has_goal_child(int var) const {

	vector<int> successors = get_causal_graph()->get_successors(var);

	for (int ch = 0; ch < successors.size(); ch++) {
		if (is_goal_var(successors[ch])) {
			return true;
		}
	}
	return false;
}


int Problem::get_var_index(string var_name) const {
	for (int var = 0; var < variable_name.size(); var++) {
		if (var_name==variable_name[var])
			return var;
	}
	return -1;
}



void Problem::get_not_needed_variables(vector<int> vars) const {
	// Currently not used
	// Returning non-goal variables that are not ancestors of any goal

	vector<int> to_remove;
	to_remove.assign(variable_domain.size(), 1);

	// For each goal variable marking
	for (int i=0;i< goal.size(); i++) {
		to_remove[goal[i].first] = 0;
		vector<int> vars;
		cg->get_ancestors(goal[i].first, vars);

		for (int j=0;j< vars.size(); j++) {
			to_remove[vars[j]] = 0;
		}
	}

	for (int i=0; i < to_remove.size(); i++) {
		if (to_remove[i] == 1){
			vars.push_back(i);
		}
	}
}



void Problem::print_conditional() const {

	for(int it = 0; it < operators.size(); it++){
		vector<PrePost> pre = operators[it]->get_pre_post();
		bool condeff = false;
		for(int it2 = 0; it2 < pre.size(); it2++) {
			if (pre[it2].cond.size() > 0) {
				condeff = true;
			}
		}
		if (condeff) {
			operators[it]->dump();
		}
	}
}


void Problem::dump() const {
	cout << "Variables:" << endl;
	for(int i = 0; i < variable_domain.size(); i++)
		cout << "  " << i << ":  " << variable_name[i] << " " << variable_domain[i] << endl;

	cout << "Actions:" << endl;
	for(int i = 0; i < operators.size(); i++) {
		cout << "  ";
		operators[i]->dump();
	}

	cout << "Initial State:" << endl;
	for(int i = 0; i < variable_domain.size(); i++)
		cout << "  " << i << ":  " << (int) initial_state->get_buffer()[i] << endl;
//	initial_state->dump();

	cout << "Goals:" << endl;
	for(int i = 0; i < goal.size(); i++)
		cout << "  " << goal[i].first << ":  " << goal[i].second << endl;
/*
	cg->dump();

	cout << "Domain Transition Graphs:" << endl;
		for(int i = 0; i < dtgs.size(); i++){
			//dtgs[i]->dump2();
			dtgs[i]->dump();
		}
*/
}

void Problem::dump_SAS(const char* filename) const {
	ofstream os(filename);
	os << "begin_metric" << endl;
	os << g_use_metric << endl;
	os << "end_metric" << endl;

	os << "begin_variables" << endl;
	os << variable_domain.size() << endl;
	for(int i = 0; i < variable_domain.size(); i++)
		os << variable_name[i] << " " << variable_domain[i] << " -1" << endl;
	os << "end_variables" << endl;

	os << "begin_state" << endl;
	for(int i = 0; i < variable_domain.size(); i++)
		os << (int) initial_state->get_buffer()[i] << endl;
	os << "end_state" << endl;

	os << "begin_goal" << endl;
	os << goal.size() << endl;
	for(int i = 0; i < goal.size(); i++)
		os << goal[i].first << " " << goal[i].second << endl;
	os << "end_goal" << endl;

	os << operators.size() << endl;
	for(int i = 0; i < operators.size(); i++) {
		operators[i]->dump_SAS(os);
	}
	os << axioms.size() << endl;
	for(int i = 0; i < axioms.size(); i++) {
		axioms[i].dump_SAS(os);
	}
}

void Problem::make_single_goal() {
	// Adding a dummy goal variable
	string nm = "var99999";
	variable_domain.push_back(2);
	variable_name.push_back(nm);

	// Change initial state, add action, set goal
	int var_count = variable_domain.size();
	state_var_t* buf = new state_var_t[var_count];

	for(int i = 0; i < var_count-1; i++) {
		buf[i] = initial_state->get_buffer()[i];
	}
	buf[var_count-1] = 0;
	initial_state = new State(buf);

	vector<Prevail> prv, cond;
	for (int i = 0; i < goal.size(); i++) {
		prv.push_back(Prevail(goal[i].first,goal[i].second));
	}
	nm = "Reach " + nm;
	vector<PrePost> pre;
	pre.push_back(PrePost(var_count-1, 0, 1, cond));
	Operator* op = new Operator(false,prv,pre,nm,0);
	operators.push_back(op);

	goal.clear();
	goal.push_back(make_pair(var_count-1,1));
}

void Problem::delete_operators(){
	for(int it = 0; it < operators.size(); it++){
		if (operators[it]) delete operators[it];
	}
	operators.clear();
	for(int it = 0; it < v_operators.size(); it++){
		v_operators[it].clear();
	}
	v_operators.clear();
}

void Problem::delete_causal_graph() {
	if (cg)
		delete cg;
}

void Problem::delete_DTGs() {
//	for (int i=0;i<dtgs.size();i++) {
//		if (dtgs[i]) delete dtgs[i];
//	}
	dtgs.clear();
}
