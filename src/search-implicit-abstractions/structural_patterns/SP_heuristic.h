#ifndef SPHEURISTIC_H_
#define SPHEURISTIC_H_

#include <vector>

#include "iforks_abstraction.h"
#include "forks_abstraction.h"
#include "../heuristic.h"
#include "../problem.h"
#include "general_abstraction.h"
#include "var_projection.h"
#include "var_proj_mapping.h"
#include "mapping.h"
#include "domain_abstraction.h"
#include "solution_method.h"

#include <iostream>

class Problem;

class SPHeuristic: public Heuristic {
	friend class LmEnrichedHeuristic;
	int strategy;
	int singletons_strategy;
	int cost_partitioning;
	int selected_ensemble;
	vector<SolutionMethod*> ensemble;

protected:
	int SIZEOFPATTERNLIMIT;
	int PERCENTAGEOFENSEMBLE;
	int STATISTICS;

	const Problem* original_problem;
	void create_binary_forks();
	void create_bounded_inverted_forks();
	void create_binary_forks_and_bounded_iforks();

//	void create_binary_fork(int v, int dom_size, bool create_singletones);
	void create_binary_fork(int v, int dom_size);
	void create_bounded_inverted_fork(int v, int dom_size);
	void create_pattern(vector<int>& pattern);
	void create_singleton(int var);

	void create_binary_forkLOO(int v, int dom_size);
	void create_bounded_inverted_forkDGV(int v, int bound, int dom_size);
	void create_inverted_fork_all_paths(int v, int dom_size);
	void create_bounded_inverted_fork_check_paths(int v, int bound, int paths_bound, int dom_size);

    void set_uniform_representatives_cost();


	Domain* create_LOO_domain(int var, int to_leave, int dom_size) const;
	Domain* create_id_domain(int var, int dom_size) const;
	Domain* create_DGV_domain(int var, vector<int>& distances, int lb, int ub) const;

	void create_ensemble_from_file(istream &in);
    void set_smart_representatives_cost();
    void set_smart_uniform_representatives_cost();

	virtual void add_ensemble_member(SolutionMethod* membr) {
//		cout << "Putting in position " << ensemble.size() << " member " << membr << endl;
		ensemble.push_back(membr);
		}

//	virtual SolutionMethod* add_binary_fork(Domain* abs_domain);
//	virtual SolutionMethod* add_bounded_inverted_fork(Domain* abs_domain);
	virtual SolutionMethod* add_pattern(vector<int>& pattern);

	virtual SolutionMethod* add_binary_fork(GeneralAbstraction* abs);
	virtual SolutionMethod* add_bounded_inverted_fork(GeneralAbstraction* abs);
	virtual SolutionMethod* add_pattern(GeneralAbstraction* abs);

	virtual SolutionMethod* add_binary_fork(ForksAbstraction* f, Domain* abs_domain);
	virtual SolutionMethod* add_bounded_inverted_fork(IforksAbstraction* ifork, Domain* abs_domain);

	void deactivate_all();
public:
	SPHeuristic(bool use_cache=false);
	SPHeuristic(const Problem* prob, bool use_cache=false);

	virtual void print_statistics() const { };
	void create_ensemble();
	virtual int compute_heuristic(const State& state);
	void get_ensemble_values(const State& state, vector<double>& vals);

	virtual ~SPHeuristic();
	bool is_heuristic_applicable() const ;

	void set_selected_ensemble_strategy(int str) { selected_ensemble = str;}
	int get_selected_ensemble_strategy() {return selected_ensemble;}
	void set_strategy(int str) { strategy = str;}
	int get_strategy() {return strategy;}
	void set_singletons_strategy(int s) {singletons_strategy = s;}
	int get_singletons_strategy() {return singletons_strategy;}

	void set_cost_partitioning_strategy(int part) {cost_partitioning = part;}
	int get_cost_partitioning_strategy() {return cost_partitioning;}

	void set_statistics_level(int level) {STATISTICS = level;}
	void set_percentage_of_ensemble(int p) {PERCENTAGEOFENSEMBLE = p;}
	int get_percentage_of_ensemble() {return PERCENTAGEOFENSEMBLE;}
	void set_minimal_size_for_non_projection_pattern(int sz) {SIZEOFPATTERNLIMIT = sz;}
	int get_minimal_size_for_non_projection_pattern() {return SIZEOFPATTERNLIMIT;}
//	int get_statistics_level() {return STATISTICS;}

    virtual void initialize();
	SolutionMethod* get_ensemble_member(int ind) {return ensemble[ind];}
	int get_ensemble_size() {return ensemble.size();}
	int get_num_vars();
	int get_num_active_vars();

	virtual int get_number_of_unsolved_states() const { exit(1);};
	void solve_all();
	void solve_all_and_remove_operators();
	void check_cost_partition();
	void print_abstract_operators();

};


#endif /* SPHEURISTIC_H_ */
