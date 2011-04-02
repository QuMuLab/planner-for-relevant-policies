#ifndef LPHEURISTIC_H_
#define LPHEURISTIC_H_

//#ifdef USE_MOSEK
#ifdef USE_LP

#include <vector>

#include "forks_abstraction.h"
#include "SP_heuristic.h"
//#include "offline_heuristic.h"
#include "../problem.h"
#include "general_abstraction.h"
#include "var_projection.h"
#include "var_proj_mapping.h"
#include "mapping.h"
#include "domain_abstraction.h"
#include "LPConstraint.h"

#include <iostream>
#include "MOSEK_solver.h"
#include "OSI_solver.h"

typedef MOSEK_solver LPSolver;
//typedef OSI_solver LPSolver;

class Problem;
//class OfflineHeuristic;

class LPHeuristic: public SPHeuristic {
	int unsolved_states;
	LPSolver* prob;

protected:

	int compute_Optimal_heuristic(const State& state);
	int compute_Additive_heuristic(const State& state);

	void build_LP_objective(vector<ConstraintVar*>& obj_func);
	void build_LP_objective(int ind, vector<ConstraintVar*>& obj_func);
	int build_LP_constraints(vector<LPConstraint*> &constr, const State& state);
	int build_LP_constraints(vector<LPConstraint*> &constr, int ind, const State& state);


	int generate_general_cost_constraints(vector<LPConstraint*>& constr);
	int generate_uniform_cost_constraints(vector<LPConstraint*>& constr);
	void calculate_representatives_cost(const vector<Operator*>& ops, vector<double>& costs);
	void update_costs_from_solution(Solution* sol);

	int generate_cost_constraints(vector<LPConstraint*>& constr, int ind,
			const vector<Operator*>& ops, vector<double>& costs);

	virtual SolutionMethod* add_pattern(vector<int>& pattern);

	virtual SolutionMethod* add_binary_fork(GeneralAbstraction* abs);
	virtual SolutionMethod* add_bounded_inverted_fork(GeneralAbstraction* abs);
	virtual SolutionMethod* add_pattern(GeneralAbstraction* abs);

	virtual SolutionMethod* add_binary_fork(ForksAbstraction* fork, Domain* abs_domain);
	virtual SolutionMethod* add_bounded_inverted_fork(IforksAbstraction* ifork, Domain* abs_domain);

public:
	LPHeuristic(bool use_cache=false);
	LPHeuristic(const Problem* prob, bool use_cache=false);
	virtual ~LPHeuristic();

	virtual int compute_heuristic(const State& state);

    virtual int get_number_of_unsolved_states() const { return unsolved_states;};
	virtual void print_statistics() const;

//	void set_ensemble(OfflineHeuristic* offh);

};
#endif
#endif /* LPHEURISTIC_H_ */
