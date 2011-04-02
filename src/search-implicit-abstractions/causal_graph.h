#ifndef CAUSAL_GRAPH_H
#define CAUSAL_GRAPH_H

#include <algorithm>
#include <iosfwd>
#include <map>
#include <vector>
#include "operator.h"
using namespace std;


class CausalGraph {
  vector<vector<int> > arcs;
  vector<vector<int> > inverse_arcs;
  vector<vector<int> > edges;
  void create(int num_vars, vector<Operator*>& ops, bool for_HHH = false);
  void add_arcs(int from, int to);
  CausalGraph(const CausalGraph&);
public:
  CausalGraph(istream &in);
  CausalGraph(int num_vars, vector<Operator*>& ops, bool for_HHH = false) {  // Added by Michael
	  create(num_vars, ops, for_HHH);
  }
//  CausalGraph(const CausalGraph&) {  // Added by Michael
//	  cout << "Causal Graph Copy constructor not implemented" << endl;
//  }

  ~CausalGraph() {}
  const vector<int> &get_successors(int var) const;
  const vector<int> &get_predecessors(int var) const;
  const vector<int> &get_neighbours(int var) const;
  void get_ancestors(int var, vector<int> &ancestors) const;  // Added by Michael

  void dump() const;
};

#endif
