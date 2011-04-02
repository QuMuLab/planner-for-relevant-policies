//#ifdef USE_MOSEK
#ifdef USE_LP

#include "LP_heuristic.h"
#include "var_projection.h"
#include <vector>
#include "../problem.h"
#include "../globals.h"
#include "general_abstraction.h"
#include "var_proj_mapping.h"
#include <iostream>
#include "LP_projection_gen.h"
#include "LP_binary_forks.h"
#include "LP_binary_forks_KD.h"
#include "LP_binary_forks_bounds.h"
#include "LP_bounded_ifork_gen.h"

#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include "../causal_graph.h"
#include "LPConstraint.h"


LPHeuristic::LPHeuristic(bool use_cache)
    : SPHeuristic(use_cache) {
	unsolved_states = 0;
	prob = new LPSolver();

}

LPHeuristic::LPHeuristic(const Problem* p, bool use_cache)
    : SPHeuristic(p, use_cache) {
	unsolved_states = 0;
	prob = new LPSolver();

}


LPHeuristic::~LPHeuristic() {

//	if (prob)
//		delete prob;
//	int num_patterns = ensemble.size();
//	for (int it = 0; it < num_patterns; it++) {
//		delete ensemble[it];
//	}
}


void LPHeuristic::print_statistics() const {
//	Heuristic::print_statistics();
	cout << "Unsolved LP in " << unsolved_states << " states" << endl;
}

int LPHeuristic::compute_heuristic(const State& state)
{
	if (original_problem->is_goal(&state))
		return 0;
	int res;
	if (get_cost_partitioning_strategy() == GENERAL){
		res = compute_Optimal_heuristic(state);
	} else if (get_cost_partitioning_strategy() == UNIFORM){
		res = compute_Additive_heuristic(state);
	} else {
		// Shouldn't happen
		cout << "NO COST PARTITIONING!!!" << endl;
		exit(0);
	}

	if(unsolved_states > 0) {
		cout << "Unsolved LP in " << unsolved_states << " states" << endl;
		exit(1);
	}

	return res;
}

int LPHeuristic::compute_Optimal_heuristic(const State& state)
{
//	if (STATISTICS>=3) {
//		cout << "Start building LP [t=" << g_timer << "]" << endl;
//	}
	/*
	deactivate_all();

    srand(time(0));  // Initialize random number generator.
    // Selecting patterns from ensemble to participate in computing heuristic
    int counter = 0;
    while (counter == 0) {
    	for (int it = 0; it < get_ensemble_size(); it++) {
    		SolutionMethod* membr = get_ensemble_member(it);
    		if (!membr->get_mapping()->is_goal_in_abstraction(&state)){
    			int pstg = (rand() % 100) + 1;
    			if (pstg <= PERCENTAGEOFENSEMBLE) {
    				membr->set_abstraction_index(counter);
    				membr->activate();
    				counter += membr->get_num_vars();
    			}
    		}
    	}
    }
    */
//    int n_cols = counter;
	int n_cols = get_num_active_vars();
	vector<LPConstraint*> constr;
//	if (STATISTICS>=3) {
//		cout << "Start building constraints  [t=" << g_timer << "]" << endl;
//	}
	vector<ConstraintVar*> obj_func;
	build_LP_objective(obj_func);
	int num_nonzeros = build_LP_constraints(constr, state);
	// Fill the cost-constraints
	num_nonzeros += generate_general_cost_constraints(constr);

//	if (STATISTICS>=3) {
//		cout << "End building constraints, start solving  [t=" << g_timer << "]" << endl;
//	}

	// Counting the number of rows
	int n_rows = constr.size();
	prob->set_size(n_cols,n_rows,num_nonzeros);
	prob->initialize();

	Solution* sol = new Solution();

	double val = prob->solve(obj_func,constr,sol);

//	if (STATISTICS>=2) {
//		cout << "Evaluation: " << val << endl;
//	}
//	if (STATISTICS>=3) {
//		cout << "Done Solving LP, start Freeing memory [t=" << g_timer << "]" << endl;
//	}

	update_costs_from_solution(sol);

	// Freeing memory;
	prob->free_mem();

	delete sol;
	for (int i = 0; i < constr.size(); i++) {
		if (!constr[i]->tokeep()) {
			constr[i]->free_mem();
			delete constr[i];
		}
	}

	for (int i = 0; i < obj_func.size(); i++) {
		delete obj_func[i];
	}

//	if (STATISTICS>=3) {
//		cout << "Done  [t=" << g_timer << "]" << endl;
//	}

	if (val >= LP_INFINITY)
		return DEAD_END;

	if (val == 0.0) {
		unsolved_states++;
		return 1.0;
	}

	if (val > 0.0) {
		return ceil(val-0.01); // TODO: double-check the epsilon
	}
	cout << "Weird..." << endl;
	return 1;

}


int LPHeuristic::compute_Additive_heuristic(const State& state)
{

	double total_val = 0.0;
	/*
	deactivate_all();
    srand(time(0));  // Initialize random number generator.
    // Selecting patterns from ensemble to participate in computing heuristic

    bool is_empty = true;
    while (is_empty) {
    	for (int it = 0; it < get_ensemble_size(); it++) {
    		SolutionMethod* membr = get_ensemble_member(it);
    		if (!membr->get_mapping()->is_goal_in_abstraction(&state)){
    			int pstg = (rand() % 100) + 1;
    			if (pstg <= PERCENTAGEOFENSEMBLE) {
    				membr->set_abstraction_index(0);
    				membr->activate();
    				is_empty = false;
    			}
    		}
    	}
    }
    */

	// Setting the cost partitioning
	const vector<Operator*> &ops = original_problem->get_operators();

	vector<double> costs;
	calculate_representatives_cost(ops,costs);


	int total_n_cols= 0;
	int total_n_rows= 0;
	int total_n_nonzeros= 0;

	for (int ind=0;ind < get_ensemble_size();ind++) {
		SolutionMethod* membr = get_ensemble_member(ind);

		if (!membr->is_active())
			continue;

//		if (STATISTICS>=3) {
//			cout << "Member " << ind << ": Start building LP [t=" << g_timer << "]" << endl;
//		}

		int n_cols = membr->get_num_vars();
		vector<LPConstraint*> constr;
//		if (STATISTICS>=3) {
//			cout << "Start building constraints  [t=" << g_timer << "]" << endl;
//		}
		vector<ConstraintVar*> obj_func;
		build_LP_objective(ind, obj_func);

		int num_nonzeros = build_LP_constraints(constr,ind,state);
		// Setting the cost constraints
		num_nonzeros += generate_cost_constraints(constr, ind, ops, costs);

//		if (STATISTICS>=3) {
//			cout << "End building constraints, start solving  [t=" << g_timer << "]" << endl;
//		}

		// Counting the number of rows
		int n_rows = constr.size();
//		MOSEK_solver* prob = new MOSEK_solver();
		prob->set_size(n_cols,n_rows,num_nonzeros);
		prob->initialize();
		double val = prob->solve(obj_func,constr,NULL);

//		if (STATISTICS) {
//			cout << "Initializing LP with "<< n_cols << " variables and " << n_rows << " constraints, and " <<  num_nonzeros << " nonzeros." << endl;
//		}
		total_n_cols += n_cols;
		total_n_rows += n_rows;
		total_n_nonzeros += num_nonzeros;

//		if (STATISTICS>=3) {
//			cout << "Done Solving LP, start Freeing memory [t=" << g_timer << "]" << endl;
//		}
		// Freeing memory;
		prob->free_mem();
		for (int i = 0; i < constr.size(); i++) {
			if (!constr[i]->tokeep()) {
				constr[i]->free_mem();
				delete constr[i];
			}
		}

		for (int i = 0; i < obj_func.size(); i++) {
			delete obj_func[i];
		}

//		if (STATISTICS>=3) {
//			cout << "Done  [t=" << g_timer << "]" << endl;
//		}

		if (val >= LP_INFINITY) return DEAD_END;

		total_val+=val;
	}

//	if (STATISTICS>=2) {
//		cout << "Initializing LP with "<< total_n_cols << " variables and " << total_n_rows << " constraints, and " <<  total_n_nonzeros << " nonzeros." << endl;
//	}

	if (total_val > 0.0) {
		return ceil(total_val-0.01); // TODO: double-check the epsilon
	}
	unsolved_states++;
	return 1;

}

void LPHeuristic::build_LP_objective(vector<ConstraintVar*>& obj_func) {

	for (int ind=0;ind < get_ensemble_size();ind++) {
		if (!get_ensemble_member(ind)->is_active())
			continue;
		build_LP_objective(ind, obj_func);
	}
}

void LPHeuristic::build_LP_objective(int ind, vector<ConstraintVar*>& obj_func) {

	SolutionMethod* membr = get_ensemble_member(ind);
//	int index = get_ensemble_member(ind)->get_abstraction_index();
	vector<ConstraintVar*> obj;
	membr->get_objective(obj);
//	cout << "Function get_objective returned " << obj.size() << " variables in objective" << endl;

	for (int i =0; i < obj.size(); i++) {
		obj_func.push_back(new ConstraintVar(membr->get_abstraction_index()+obj[i]->var,obj[i]->val));
	}
}


int LPHeuristic::build_LP_constraints(vector<LPConstraint*> &constr, const State& state) {

	int num_nonzeros = 0;
	for (int ind=0;ind < get_ensemble_size();ind++) {
		if (!get_ensemble_member(ind)->is_active())
			continue;
		// Fill the constraints

		num_nonzeros += build_LP_constraints(constr, ind, state);
	}
	return num_nonzeros;
}

int LPHeuristic::build_LP_constraints(vector<LPConstraint*> &constr, int ind, const State& state) {
	int ret = get_ensemble_member(ind)->append_constraints(&state, constr);
//	cout << "Adding " << ret << " constraints" << endl;
	return ret;
}


//////////////////////////////////////////////////////////////////////////////////

int LPHeuristic::generate_general_cost_constraints(vector<LPConstraint*>& constr) {
	int res = 0;
	// Fill the cost-constraints
	const vector<Operator*> &ops = original_problem->get_operators();

	int num_ops = ops.size();
	for (int a_i = 0; a_i < num_ops; a_i++) {

		LPConstraint* lpc = new LPConstraint(0.0,ops[a_i]->get_double_cost(),false);

		int tmp_res = 0;
		for (int ind=0;ind < get_ensemble_size();ind++) {
			SolutionMethod* membr = get_ensemble_member(ind);
			if (!membr->is_active())
				continue;
			int index = membr->get_abstraction_index();
			Mapping* map = membr->get_mapping();
			vector<Operator*> abs_ops;
			map->get_abs_operators(ops[a_i], abs_ops);
			int num_abs_ops = abs_ops.size();
			if (num_abs_ops > 0) {
				for (int j = 0; j < num_abs_ops; j++) {
					int w_ind = index + membr->w_var(abs_ops[j]);
					lpc->add_val(w_ind, 1.0);
				}
			}
			tmp_res += num_abs_ops;
		}
		if (tmp_res > 0) {
			lpc->finalize();
			constr.push_back(lpc);
//			lpc->dump();
		} else {
			delete lpc;
		}
		res+= tmp_res;

	}
	return res;
}


int LPHeuristic::generate_uniform_cost_constraints(vector<LPConstraint*>& constr) {
	int res = 0;
	// Fill the cost-constraints
	const vector<Operator*> &ops = original_problem->get_operators();

	vector<double> costs;
	calculate_representatives_cost(ops,costs);

	for (int ind=0;ind < get_ensemble_size();ind++) {
		if (!get_ensemble_member(ind)->is_active())
			continue;

		res += generate_cost_constraints(constr, ind, ops, costs);
	}

	return res;

}


void LPHeuristic::calculate_representatives_cost(const vector<Operator*>& ops, vector<double>& costs) {

	int num_ops = ops.size();
	for (int a_i = 0; a_i < num_ops; a_i++) {

		// Counting the number of actions
		vector<Operator*> abs_ops;
		for (int ind=0;ind < get_ensemble_size();ind++) {
			SolutionMethod* membr = get_ensemble_member(ind);
			if (!membr->is_active())
				continue;
			membr->get_mapping()->get_abs_operators(ops[a_i],abs_ops);
		}
		int num_actions = abs_ops.size();
		if (num_actions > 0) {
			double abs_cost = ops[a_i]->get_double_cost() / num_actions;
			costs.push_back(abs_cost);
		} else {
			costs.push_back(LP_INFINITY);
		}

	}
}


void LPHeuristic::update_costs_from_solution(Solution* sol) {
	for (int ind=0;ind < get_ensemble_size();ind++) {
		SolutionMethod* membr = get_ensemble_member(ind);
		if (!membr->is_active())
			continue;

		int index = membr->get_abstraction_index();
		Mapping* map = membr->get_mapping();
		const vector<Operator*> &abs_ops = map->get_abstract()->get_operators();

		int num_abs_ops = abs_ops.size();
		for (int j = 0; j < num_abs_ops; j++) {
			int w_ind = index + membr->w_var(abs_ops[j]);
			double c = sol->get_value(w_ind);
			if (c < 0.0000001)
				c = 0.0;

			abs_ops[j]->set_double_cost(c);

//			cout << "---> " << index << ", " << membr->w_var(abs_ops[j]) <<
//			     " (" << w_ind << "): "<< c << endl;
		}
//		map->get_abstract()->dump();

//		if (STATISTICS>=4) {
//			map->get_abstract()->dump();
//		}
	}
}




int LPHeuristic::generate_cost_constraints(vector<LPConstraint*>& constr, int ind,
		const vector<Operator*>& ops, vector<double>& costs) {
	int res = 0;
	int num_ops = ops.size();

	SolutionMethod* membr = get_ensemble_member(ind);
	// Entering constraints fixing the costs
	int index = membr->get_abstraction_index();
	Mapping* map = membr->get_mapping();

	for (int a_i = 0; a_i < num_ops; a_i++) {
		vector<Operator*> abs_ops;
		map->get_abs_operators(ops[a_i],abs_ops);
		int num_abs_ops = abs_ops.size();
		for (int j = 0; j < num_abs_ops; j++) {
			int w_ind = membr->w_var(abs_ops[j]);

			LPConstraint* lpc = new LPConstraint(costs[a_i],costs[a_i],false);
			lpc->add_val(index + w_ind, 1.0);
			lpc->finalize();

			constr.push_back(lpc);
		}
		res += num_abs_ops;
	}
	return res;
}



///////////////////////////////////////////////////////////////////////////////
SolutionMethod* LPHeuristic::add_binary_fork(GeneralAbstraction* abs) {
	return new LPBinaryForks_b(abs);
}

SolutionMethod* LPHeuristic::add_bounded_inverted_fork(GeneralAbstraction* abs) {
	return new LPBoundedIfork(abs);
}

SolutionMethod* LPHeuristic::add_pattern(GeneralAbstraction* abs) {
	return new LPProjection(abs);
}

SolutionMethod* LPHeuristic::add_binary_fork(ForksAbstraction* fork, Domain* abs_domain) {
	return new LPBinaryForks_b(fork, abs_domain);
}

SolutionMethod* LPHeuristic::add_bounded_inverted_fork(IforksAbstraction* ifork, Domain* abs_domain) {
	return new LPBoundedIfork(ifork, abs_domain);
}


SolutionMethod* LPHeuristic::add_pattern(vector<int>& pattern) {
//	LPProjectionKD* ptrn = new LPProjectionKD(pattern);
	LPProjection* ptrn = new LPProjection(pattern);
	// Creating the abstraction
	ptrn->create(original_problem);
	ptrn->set_abstraction_type(PATTERN);
//	cout << "Adding ensemble member " << ptrn << endl;

	return ptrn;
}


///////////////////////////////////////////////////////////////////////////////


#endif
