#ifndef PROBLEM_H_
#define PROBLEM_H_

#include <vector>
#include <set>

#include "globals.h"
#include "state.h"
#include "operator.h"
#include "domain_transition_graph.h"

#include "causal_graph.h"

class Problem {

	bool is_cond;

	vector<string> variable_name;
	vector<int> variable_domain;
	const State* initial_state;
	vector<pair<int, int> > goal;
	vector<Operator*> operators;
	CausalGraph* cg;
	vector<DomainTransitionGraph*> dtgs;
	vector<int> goal_vars;
	vector<vector<Operator*> > v_operators;
	vector<Operator> axioms;

private:
	void remove_conditional_effects(Operator* op, vector<Operator*>& ops);
 	void get_not_needed_variables(vector<int> vars) const;          // Not used for now.
	void make_SAS_operators(Operator* op, vector<Operator*>& ops);  // Not used for now.
	bool set_nonconditional();
	Problem(const Problem& p);

public:
	Problem(bool translator_cg = false);

	Problem(vector<string> var_name,
			vector<int> var_domain,
			const State* init_state,
			vector<pair<int, int> > g,
			vector<Operator*> ops, vector<Operator> axioms,
			bool translator_cg=false);

	virtual ~Problem();

	void create_problem(vector<string>& var_name,
			vector<int>& var_domain,
			const State* init_state,
			vector<pair<int, int> >& g,
			vector<Operator*>& ops, vector<Operator>& axioms);


	const State* get_initial_state() const {return initial_state;}
	bool is_goal(const State* state) const;

	void generate_state_transition_graph(vector<vector<int> >& states) const;
	void get_applicable_states(Operator* op, vector<int> & vals) const;

    const std::vector<Operator*> &get_var_actions(int var) const {return v_operators[var];}
    const std::vector<string> &get_variable_names() const {return variable_name;}
	const std::vector<int> &get_variable_domains() const {return variable_domain;}
	const std::vector<Operator*> &get_operators() const {return operators;}

	void get_goal(vector<pair<int, int> >& g) const {g = goal;}
	void get_goal_vals(vector<int>& g) const {g = goal_vars;}
	string get_variable_name(int var) const {return variable_name[var];}
	int get_variable_domain(int var) const {return variable_domain[var];}
	int get_vars_number() const {return variable_name.size();}
	int get_actions_number() const {return operators.size();}
	vector<Operator> get_axioms() const{return axioms;}
	CausalGraph* get_causal_graph() const {return cg;}
	void get_DTGs(vector<DomainTransitionGraph*>& tgs) const {tgs = dtgs;}

	void set_causal_graph(CausalGraph* causalg) {cg = causalg;}
	void set_DTGs(vector<DomainTransitionGraph*>& tgs) {dtgs = tgs;}

	void get_domain_decomposition_by_distance(int v, int val, vector<vector<int> >& vals, vector<int>& len_from_val) const;
	void get_domain_values_by_distance_to_goal(int v, vector<vector<int> >& vals, vector<int>& len_to_goal) const;
	void get_cycle_free_paths_by_length(int v, int length, vector<vector<Operator*> >& paths) const;

	void get_all_cycle_free_paths_to_goal(int v, vector<vector<Operator*> >& paths) const;
	int get_estimated_number_of_all_cycle_free_paths_to_goal(int v) const;
	bool is_estimated_number_of_all_cycle_free_paths_to_goal_bounded(int v, int bound) const;

	void fill_DTG(int var);

	int get_action_index(const Operator* a) const {return a->get_index();}

	Operator* get_action_by_index(int index) const {return operators[index];}

	bool is_nonconditional() const {return is_cond;}

	void print_conditional() const;

	bool has_goal_child(int var) const;

	int get_goal_val(int var) const {return goal_vars[var];}
	bool is_goal_var(int var) const {return (-1 != get_goal_val(var));}

	int get_var_index(string var_name) const;

 	void set_operators_to_uniform_cost();
 	void increase_operators_cost();

 	void delete_operators();
 	void delete_causal_graph();
 	void delete_DTGs();

 	int get_mem_size() const ;
    void dump() const;
    void dump_SAS(const char* filename) const;
    void make_single_goal();

};

#endif /* PROBLEM_H_ */
