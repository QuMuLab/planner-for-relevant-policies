#ifndef BOUNDED_IFORK_GEN_H_
#define BOUNDED_IFORK_GEN_H_

#include "solution_method.h"
#include "bounded_iforks.h"
#include "iforks_abstraction.h"
#include "ifork_root_path.h"
#include <cfloat>
#include <list>

/* This class describes solution for inverted forks with bounded root domain.
 */


class BoundedIfork: public SolutionMethod {

	int max_domain;
	int num_parents;


	void create_non_dominating_paths(double* sol, vector<vector<int> >& to_keep, bool remove_dominating);
	double calculate_supp_cost(double* sol, int v, vector<int>& supp);
	void precalculate_path(double* sol, IforkRootPath* path);
	void sort_and_remove_dominating_paths(int root_val, list<IforkRootPath*>& paths, bool remove_dominating);

protected:
	vector<IforkRootPath*>* root_paths_values;
	int number_of_d_variables, number_of_h_variables, number_of_w_var_variables;

public:
	BoundedIfork();
	BoundedIfork(GeneralAbstraction* abs);
	BoundedIfork(IforksAbstraction* ifork, Domain* abs_domain);

	virtual ~BoundedIfork();

	void initiate();
	virtual void solve() {solve_internal();}
	void solve_internal(bool remove_dominating = true);

	virtual double get_solution_value(const State* state);
//	virtual int num_d_vars() const {return num_parents*max_domain*max_domain;}

	virtual int d_var(int var, int val, int i) const;

	virtual int get_num_vars() const;
	virtual void remove_abstract_operators() {}

};

#endif /* BOUNDED_IFORK_GEN_H_ */
