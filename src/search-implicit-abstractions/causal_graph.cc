#include "causal_graph.h"
#include "globals.h"

#include <iostream>
#include <cassert>
using namespace std;

CausalGraph::CausalGraph(istream &in) {
  check_magic(in,"begin_CG");
  int var_count = g_variable_domain.size();
  arcs.resize(var_count);
  inverse_arcs.resize(var_count);
  edges.resize(var_count);
  for(int from_node = 0; from_node < var_count; from_node++) {
    int num_succ;
    in >> num_succ;
    arcs[from_node].reserve(num_succ);
    for(int j = 0; j < num_succ; j++) {
      // weight not needed so far
      int to_node, weight;
      in >> to_node;
      in >> weight;
      add_arcs(from_node, to_node);  // Michael: Replaced to reduce code duplication
//      arcs[from_node].push_back(to_node);
//      inverse_arcs[to_node].push_back(from_node);
//      edges[from_node].push_back(to_node);
//      edges[to_node].push_back(from_node);
    }
  }
  check_magic(in, "end_CG");

  for(int i = 0; i < var_count; i++) {
    sort(edges[i].begin(), edges[i].end());
    edges[i].erase(unique(edges[i].begin(), edges[i].end()), edges[i].end());
  }
}

const vector<int> &CausalGraph::get_successors(int var) const {
  return arcs[var];
}

const vector<int> &CausalGraph::get_predecessors(int var) const {
  return inverse_arcs[var];
}

const vector<int> &CausalGraph::get_neighbours(int var) const {
  return edges[var];
}

void CausalGraph::dump() const {
  cout <<"Causal graph: "<< endl;
  for(int i = 0; i < arcs.size(); i++) {
    cout << "dependent on var " << g_variable_name[i] << ": " << endl;
    for(int j = 0; j < arcs[i].size(); j++)
      cout <<"  "<< g_variable_name[arcs[i][j]] << ",";
    cout << endl;
    }
}

// TODO: put acyclicity in input
//bool CausalGraph::is_acyclic() const {
//  return acyclic;
//}

// Added by Michael
void CausalGraph::create(int num_vars, vector<Operator*>& ops, bool for_HHH) {
	// Going over the operators, adding the arcs multiple times, and then removing non-unique.

	arcs.resize(num_vars);
	inverse_arcs.resize(num_vars);
	edges.resize(num_vars);

	int num_ops = ops.size();
	for(int a = 0; a < num_ops; a++){
		vector<Prevail> prv = ops[a]->get_prevail();
		vector<PrePost> pre = ops[a]->get_pre_post();

		// Arc (u,v)
		for(int v = 0; v < pre.size(); v++){
			// Add the condition of this effect
			for(int u = 0; u < pre[v].cond.size(); u++){
				add_arcs(pre[v].cond[u].var,pre[v].var);
			}
			// Add the prevail condition of the action
			for(int u = 0; u < prv.size(); u++){
				add_arcs(prv[u].var,pre[v].var);
			}
			// Add the non-prevail precondition of the action
			for(int u = 0; u < pre.size(); u++){
				if ((u!=v) && ((-1 != pre[u].pre) || (!for_HHH))) {
					add_arcs(pre[u].var, pre[v].var);
				}
			}
		}
	}

	for(int i = 0; i < num_vars; i++) {
		sort(arcs[i].begin(), arcs[i].end());
		arcs[i].erase(unique(arcs[i].begin(), arcs[i].end()), arcs[i].end());
		sort(inverse_arcs[i].begin(), inverse_arcs[i].end());
		inverse_arcs[i].erase(unique(inverse_arcs[i].begin(),
				inverse_arcs[i].end()), inverse_arcs[i].end());

		sort(edges[i].begin(), edges[i].end());
		edges[i].erase(unique(edges[i].begin(), edges[i].end()), edges[i].end());
	}
}
void CausalGraph::add_arcs(int from, int to) {
	// Warning: use at your own risk.
	if (from==to)
		return;

	arcs[from].push_back(to);
	inverse_arcs[to].push_back(from);
	edges[from].push_back(to);
	edges[to].push_back(from);
}

/*
void CausalGraph::create(int num_vars, vector<Operator*>& ops, bool for_HHH) {

	arcs.resize(num_vars);
	inverse_arcs.resize(num_vars);
	edges.resize(num_vars);

	int** A = new int*[num_vars];

	for(int i = 0; i < num_vars; i++){
		A[i] = new int[num_vars];
		for(int j = 0; j < num_vars; j++){
			A[i][j] = 0;
		}
	}
	int num_ops = ops.size();
	for(int a = 0; a < num_ops; a++){
		vector<Prevail> prv = ops[a]->get_prevail();
		vector<PrePost> pre = ops[a]->get_pre_post();

		// Arc (u,v)
		for(int v = 0; v < pre.size(); v++){
			// Add the condition of this effect
			for(int u = 0; u < pre[v].cond.size(); u++){
				A[pre[v].cond[u].var][pre[v].var] = 1;
			}
			// Add the prevail condition of the action
			for(int u = 0; u < prv.size(); u++){
				A[prv[u].var][pre[v].var] = 1;
			}
			// Add the non-prevail precondition of the action
			for(int u = 0; u < pre.size(); u++){
				if ((u!=v) && ((-1 != pre[u].pre) || (!for_HHH))) {
					A[pre[u].var][pre[v].var] = 1;
				}
			}
		}
	}
	for(int i = 0; i < num_vars; i++){
		for(int j = 0; j < num_vars; j++){
			if (i==j)
				continue;
			if (A[i][j] > 0) {
				arcs[i].push_back(j);
				inverse_arcs[j].push_back(i);
				edges[i].push_back(j);
				edges[j].push_back(i);
			}
		}
	}

	for(int i = 0; i < num_vars; i++) {
		delete [] A[i];
		sort(edges[i].begin(), edges[i].end());
		edges[i].erase(unique(edges[i].begin(), edges[i].end()), edges[i].end());
	}
	delete [] A;

}
*/
void CausalGraph::get_ancestors(int var, vector<int> &ancestors) const {
	if (inverse_arcs[var].size() == 0) {
		ancestors = inverse_arcs[var];
		return;
	}
	int num_vars = inverse_arcs.size();
	vector<int> all_ancestors;
	all_ancestors.assign(num_vars,0);
	all_ancestors[var] = 1;

	bool done = false;

	vector<int> front;
	front.push_back(var);

	while (!done) {
		// Set the new front
		vector<int> new_front;
		for (int i=0; i < front.size(); i++) {
			for (int j=0; j < inverse_arcs[front[i]].size(); j++) {
				new_front.push_back(inverse_arcs[front[i]][j]);
			}
		}
		front = new_front;

		done = true;
		// Update the front
		for (int i=0; i < front.size(); i++) {
			if (all_ancestors[front[i]] == 0)
				done = false;
			all_ancestors[front[i]] = 1;
		}
	}

	for (int i=0; i < num_vars; i++) {
		if (all_ancestors[i] > 0)
			ancestors.push_back(i);
	}
}

