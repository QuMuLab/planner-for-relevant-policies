#ifndef IFORK_ROOT_PATH_H_
#define IFORK_ROOT_PATH_H_

#include <vector>
#include "../operator.h"
#include <stdio.h>
#include "LPConstraint.h"

class IforkRootPath {
	vector<Operator*> path;
	vector<int> first_needed;
	vector<pair<int,int> > first_needed_pairs;
	double cost;
	int num_vars;
	// For LP
	LPConstraint* lpc;
	bool is_borrowed_lpc;
public:
	IforkRootPath();
	IforkRootPath(int sz);
	IforkRootPath(IforkRootPath* cp);

	virtual ~IforkRootPath();

//	void get_path(vector<Operator*>& p) const;
	const vector<Operator*>& get_path() const {return path;}
	void set_path(vector<Operator*>& p);

	int get_first_needed(int v) const;
	void set_first_needed(int v, int val);
	void set_num_vars(int vars);
	int get_num_vars();
	int get_path_size() const;
	void get_path_support(int v, vector<int>& support) const;

	void get_applicable_vals(int root_bound, vector<int>& vals) const;
	bool is_dominated(IforkRootPath* path_b) const;

	double get_path_cost() const;
	double get_needed_cost() const;
	void set_needed_cost(double c);

	void set_first_needed_pairs();
//	void get_first_needed_pairs(vector<pair<int,int> >& pairs);
	const vector<pair<int,int> > &get_first_needed_pairs() const {return first_needed_pairs;}

	LPConstraint* get_LP_constraint();
	void set_LP_constraint(LPConstraint* c);
	void clear_path_actions() {path.clear();}

	void dump() const;
    Operator* get_first_operator() const {
    assert (path.size() > 0);
    return path[0];
    }
};

#endif /* IFORK_ROOT_PATH_H_ */
