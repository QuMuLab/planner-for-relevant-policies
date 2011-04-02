#include "lm_enriched_heuristic.h"
#include "globals.h"
#include "operator.h"
#include "successor_generator.h"
#include "structural_patterns/SP_globals.h"

#include <sstream>
#include <math.h>

//#define epsilon 0.01
#define INITVAL 1
#define GOALVAL 0


LmEnrichedHeuristic::LmEnrichedHeuristic(LandmarksGraph& l, const char *arg, bool use_cache) :
	Heuristic(use_cache), lgraph(l), lm_status_manager(lgraph), h_arg(arg) {
//	name = h_arg;//"LM_ENRICHED";
	original_problem = new Problem();
}

LmEnrichedHeuristic::LmEnrichedHeuristic(const Problem* prob, LandmarksGraph& l, const char *arg, bool use_cache) :
	Heuristic(use_cache), lgraph(l), lm_status_manager(lgraph), original_problem(prob), h_arg(arg) {
//	name = h_arg;//"LM_ENRICHED";
}

LmEnrichedHeuristic::~LmEnrichedHeuristic() {
	delete en_state;
	delete en_prob;
	delete h;
}

int LmEnrichedHeuristic::compute_heuristic(const State& state) {
	// Get landmarks that have been true at some point (put into
	// "reached_lms") and their cost

	if (original_problem->is_goal(&state))
		return 0;

	if (lm_status_manager.update_lm_status(state))
		return DEAD_END;


	// Get enriched state from state
	update_enriched_state(state);
	h->evaluate(*en_state);
	if (h->is_dead_end())
		return DEAD_END;
	return h->get_heuristic();
}

void LmEnrichedHeuristic::initialize() {

	set_needed_landmarks();

	lm_status_manager.set_landmarks_for_initial_state(*original_problem->get_initial_state());
	lm_status_manager.update_lm_status(*original_problem->get_initial_state());
	const char *c = h_arg;
//	h_arg++;

	// Create the enriched problem and the heuristic
	if (c[0] == 'a') {
		bool del_unreached = true;
		for(int i=1; c[i] != 0; i++) {
			if (c[i] == 'U')
				del_unreached = false;
		}
		en_prob = build_enriched_problem(true, del_unreached);
		h = build_fd_heuristic(h_arg+1, en_prob);
	} else if (c[0] == 's'){
		en_prob = build_enriched_problem(false, false);
		h = build_sp_heuristic(h_arg+1, en_prob);
	} else {
		cout << "Unknown option: " << c[0] << " for enriched heuristic." << endl;
		exit(1);
	}
//	en_prob->write_everything();
//	en_prob->dump();
//	h->initialize();
}

bool LmEnrichedHeuristic::reach_state(const State& parent_state,
		const Operator &op, const State& state) {
    lm_status_manager.update_reached_lms(parent_state, op, state);
	return true;
}


void LmEnrichedHeuristic::build_enriched_operators(vector<Operator*> &en_operators,
		bool create_additional_operators) {
//TODO: FIND BUG that appears on instance p04 of transport-strips-ipc6 domain.
	assert(en_operators.size() == 0);

	const vector<Operator*> ops = original_problem->get_operators();
	for (int i = 0; i < ops.size(); i++){
		en_operators.push_back(build_enriched_operator(ops[i]));
	}
	if (create_additional_operators)
		create_remove_landmarks_operators(en_operators);

}


void LmEnrichedHeuristic::build_enriched_prepost(const Operator* op, vector<PrePost>& pre) {

	pre = op->get_pre_post();
	vector<int> addition_eff_vars;//list of index of variables that should be added to pre post
	vector<vector<Prevail> > cond_effs;

	for (int j = 0; j < pre.size(); j++) {
		// Check if this action changes a variable to a landmark value

		// Loop on all relevant landmarks
		int ind = original_problem->get_vars_number();
		for (set<LandmarkNode*>::const_iterator it = lgraph.get_nodes().begin(); it
				!= lgraph.get_nodes().end(); it++, ind++) {
			LandmarkNode& curr_land = **it;

			for (int k = 0; k < curr_land.vars.size(); k++) {
				// Check if this action changes a variable to a landmark value
				if (curr_land.vars[k] == pre[j].var && curr_land.vals[k]
						== pre[j].post) {
					// Need to add an effect to this action
					addition_eff_vars.push_back(ind);
					// Add also the condition to the effect (may be empty)
					cond_effs.push_back(pre[j].cond);
					break;
				}
			}
		}
	}

	// Check that no landmark was added twice to an effect.

	int l_sz = addition_eff_vars.size();
	vector<int> to_remove;
	to_remove.assign(l_sz, 0);

	for (int i = 0; i < l_sz - 1; i++) {
		//cout <<  "i= "<<  i << " size= " << addition_eff_vars.size() << endl;
		for (int j = i + 1; j < l_sz; j++) {
			if (addition_eff_vars[i] == addition_eff_vars[j]) {
				// check if condition of one is included in other
				if (prev_subseteq(cond_effs[i], cond_effs[j])) {
					to_remove[j]++;
				} else if (prev_subseteq(cond_effs[j], cond_effs[i])) {
					to_remove[i]++;
				}
			}
		}
	}

	// Add new landmarks variables to pre_post
	for (int j = 0; j < l_sz; j++) {
		if (to_remove[j] == 0) {
			vector<Prevail> cond = cond_effs[j];
//			cond.push_back(Prevail(addition_eff_vars[j],INITVAL));  // Temporal - for checking
			pre.push_back(PrePost(addition_eff_vars[j], -1, GOALVAL, cond));
		}
	}
}

void LmEnrichedHeuristic::build_enriched_variables(
		vector<string> &en_variable_name, vector<int> &en_variable_domain) {
	// Initial original variables
	int orig_vars_num = original_problem->get_vars_number();

	for (int i = 0; i < orig_vars_num; i++) {
		en_variable_name.push_back(original_problem->get_variable_name(i));
		en_variable_domain.push_back(original_problem->get_variable_domain(i));
	}

	// Loop on all relevant landmarks
	for (set<LandmarkNode*>::const_iterator it = lgraph.get_nodes().begin(); it
			!= lgraph.get_nodes().end(); it++) {
		LandmarkNode& curr_land = **it;

		string nm;
		for (int j = 0; j < curr_land.vars.size(); j++) {
			// Convert int to string
			stringstream land_val;
			land_val << curr_land.vals[j];
			if (j > 0)
				nm += "_";

			nm+= original_problem->get_variable_name(curr_land.vars[j]) + "->" + land_val.str();
		}
		en_variable_name.push_back(nm);
		en_variable_domain.push_back(2);
	}
}

State* LmEnrichedHeuristic::build_enriched_initial() {

	int orig_vars_num = original_problem->get_vars_number();
	const state_var_t* orig_init_buff = original_problem->get_initial_state()->get_buffer();
	state_var_t* init_buff = new state_var_t[orig_vars_num + lgraph.number_of_landmarks()];

	for (int i = 0; i < orig_vars_num; i++) {
		init_buff[i] = orig_init_buff[i];
	}

	// Loop on all relevant landmarks
	for (set<LandmarkNode*>::const_iterator it = lgraph.get_nodes().begin(); it
			!= lgraph.get_nodes().end(); it++, orig_vars_num++) {
		LandmarkNode& curr_land = **it;
		if (curr_land.status == lm_reached) {
			init_buff[orig_vars_num] = GOALVAL;
		} else { // status = lm_not_reached or lm_needed_again
			init_buff[orig_vars_num] = INITVAL;
		}

	}
	return new State(init_buff);
}

void LmEnrichedHeuristic::build_enriched_goal(vector<pair<int, int> >& en_goal) {

	original_problem->get_goal(en_goal);

	int orig_vars_num = original_problem->get_vars_number();
	for (int i = 0; i < lgraph.number_of_landmarks(); i++) {
		en_goal.push_back(make_pair(orig_vars_num+i, GOALVAL));
	}
}


/*
 * Update the related state in the new enriched problem-
 *  assignment of the original task variables should not change,
 *  landmark variable will get a value depending on the landmark
 *  status (achieved-1, not achieved-0).
 */
void LmEnrichedHeuristic::update_enriched_state(const State& state) {

	int orig_vars_num = original_problem->get_vars_number();

	for (int i = 0; i < orig_vars_num; i++) {
		en_state_vars[i] = state.get_buffer()[i];
	}

	for (set<LandmarkNode*>::const_iterator it = lgraph.get_nodes().begin(); it
			!= lgraph.get_nodes().end(); it++, orig_vars_num++) {
		LandmarkNode& curr_land = **it;
		if (curr_land.status == lm_reached) {
			en_state_vars[orig_vars_num] = GOALVAL;
		} else { // status = lm_not_reached or lm_needed_again
			en_state_vars[orig_vars_num] = INITVAL;
		}
	}

	/*
	// Loop on all landmarks except ones that hold in the initial or goal states
	for (int i = 0; i < en_landmarks.size(); i++) {
		if (en_landmarks[i]->status == lm_reached) {
			en_state_vars[orig_vars_num+i] = 1;
		} else { // status = lm_not_reached or lm_needed_again
			en_state_vars[orig_vars_num+i] = 0;
		}
	}
	*/

}

/*
void LmEnrichedHeuristic::build_dtgs(Problem* prob, vector<int> en_variable_domain){

	vector<DomainTransitionGraph*> dtgs = g_transition_graphs;

	//Step 1: Add DTGs for the original variables
	for(int i=g_variable_domain.size(); i < en_variable_domain.size(); i++) {
        DomainTransitionGraph *dtg = new DomainTransitionGraph(i, en_variable_domain[i]);
        dtgs.push_back(dtg);
	}
	en_prob->set_DTGs(dtgs);

	//Step 2: Add DTGs manually for the new variables. This is necessary only if the
	//        new variables have more then 2 domain values (not a binary domain).
	for(int i=g_variable_domain.size(); i < en_variable_domain.size(); i++) {
		en_prob->fill_DTG(i);
	}
}

void LmEnrichedHeuristic::init_en_landmarks(){
	assert(en_landmarks.size() == 0);
	// Loop on all landmarks except ones that hold in the initial or goal states
	for (set<LandmarkNode*>::const_iterator it = lgraph.get_nodes().begin(); it
			!= lgraph.get_nodes().end(); it++) {
		LandmarkNode& curr_land = **it;

		if (!curr_land.is_goal()
				&& !curr_land.is_true_in_state(*(original_problem->get_initial_state()))
				) {
			en_landmarks.push_back(*it);
		}
	}
}
*/

void LmEnrichedHeuristic::reset() {
	lm_status_manager.clear_reached();
	lm_status_manager.set_landmarks_for_initial_state(*g_initial_state);
}
/*
void LmEnrichedHeuristic::print_statistics() const {
	h->print_statistics();
}
*/

void LmEnrichedHeuristic::set_needed_landmarks() {
//	assert(en_landmarks.size() == 0);
	vector<LandmarkNode*> to_remove;
	// Loop on all landmarks, select only needed, remove the rest
	for (set<LandmarkNode*>::const_iterator it = lgraph.get_nodes().begin(); it
			!= lgraph.get_nodes().end(); it++) {
		LandmarkNode& curr_land = **it;

		if (curr_land.is_goal()
//				|| curr_land.is_true_in_state(*(original_problem->get_initial_state()))
				) {
			to_remove.push_back(*it);
		}
	}
	for(int i=0; i < to_remove.size(); i++) {
		lgraph.rm_landmark_node(to_remove[i]);
	}
}

///////////////////////////////////////////////////////////////////////////////////////////////

Problem* LmEnrichedHeuristic::build_enriched_problem(bool is_HHH,
		bool create_additional_operators) {


//	// Build enriched landmarks
//	init_en_landmarks();

	//Build enriched variables
	vector<string> en_variable_name;
	vector<int> en_variable_domain;
	build_enriched_variables(en_variable_name, en_variable_domain);

	// Build enriched operators
	vector<Operator*> en_operators;
	build_enriched_operators(en_operators, create_additional_operators);

	// Build enriched axioms
	vector<Operator> axioms;
	build_enriched_axioms(axioms);

//	int en_vars_size = en_variable_domain.size();
	// Build enriched initial state
	State *en_initial_state = build_enriched_initial();

	// Build enriched goal
	vector<pair<int, int> > en_goal;
	build_enriched_goal(en_goal);

	Problem* prob = new Problem(en_variable_name, en_variable_domain,
			en_initial_state, en_goal, en_operators, axioms, is_HHH);

	// Build DTGs
	vector<DomainTransitionGraph*> dtgs;
	original_problem->get_DTGs(dtgs);

	int orig_vars_num = original_problem->get_vars_number();

	//Step 1: Add DTGs for the original variables
	for(int i=orig_vars_num; i < en_variable_domain.size(); i++) {
        DomainTransitionGraph *dtg = new DomainTransitionGraph(i, en_variable_domain[i]);
        dtgs.push_back(dtg);
	}
	prob->set_DTGs(dtgs);

	//Step 2: Add DTGs manually for the new variables. This is necessary only if the
	//        new variables have more then 2 domain values (not a binary domain).
	for(int i=orig_vars_num; i < en_variable_domain.size(); i++) {
		prob->fill_DTG(i);
	}
//	lgraph.dump_dot();
	prob->dump();
	// Create en_state
	en_state_vars = new state_var_t[prob->get_vars_number()];
	en_state = new State(en_state_vars);

	return prob;
}


Operator* LmEnrichedHeuristic::build_enriched_operator(const Operator* op) {

	vector<PrePost> pre;
	build_enriched_prepost(op,pre);

	string nm;
#ifdef DEBUGMODE
	nm = op->get_name();
#endif
	Operator* new_op = new Operator(op->is_axiom(), op->get_prevail(), pre, nm, op->get_double_cost());
	new_op->set_index(op->get_index());
	return new_op;
}


void LmEnrichedHeuristic::build_enriched_axioms(vector<Operator> &en_operators) {

	vector<Operator> axi = original_problem->get_axioms();

	for (int i = 0; i < axi.size(); i++) {
		Operator* a = build_enriched_operator(&axi[i]);
		en_operators.push_back(*a);
	}
}


void LmEnrichedHeuristic::create_remove_landmarks_operators(vector<Operator*> &en_operators) {

	// Build an action for each landmark variable from 1 to 0 - to prevent non
	// reachable states in the abstractions.

	// Initial original variables
	int var_index = original_problem->get_vars_number();
	// Loop on all relevant landmarks
	int sz = lgraph.number_of_landmarks();
	for (int i = 0 ; i < sz; i++) {

		vector<Prevail> no_cond, no_prevail;
		vector<PrePost> new_pre;
		new_pre.push_back(PrePost(var_index+i,GOALVAL,INITVAL, no_cond));

		string action_name;
#ifdef DEBUGMODE
		// Convert int to string
		stringstream var_ind_name;
		var_ind_name << var_index;
		action_name = "remove landmark " + var_ind_name.str();
#endif
		Operator* en_op = new Operator(false, no_prevail, new_pre, action_name, 1.0);
		en_op->set_index(en_operators.size());
		en_operators.push_back(en_op);
	}
}


bool LmEnrichedHeuristic::prev_subseteq(vector<Prevail> prv1, vector<Prevail> prv2) {
	for (int i = 0; i < prv1.size(); i++) {
		bool var_exist = false;
		for (int j = 0; j < prv2.size(); j++) {
			if (prv1[i].var != prv2[j].var)
				continue;

			if (prv1[i].prev != prv2[j].prev)
				return false;

			var_exist = true;
			break;
		}
		if (!var_exist)
			return false;
	}
	return true;
}
