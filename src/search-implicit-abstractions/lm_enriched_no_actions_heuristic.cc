#include "lm_enriched_no_actions_heuristic.h"
#include "globals.h"
#include "operator.h"
#include "successor_generator.h"

#include <sstream>
#include <math.h>

LmEnrichedNoActionsHeuristic::LmEnrichedNoActionsHeuristic(
		LandmarksGraph& l, const char *arg, bool use_cache) :
	LmEnrichedHeuristic(l, arg, use_cache) {

}

LmEnrichedNoActionsHeuristic::LmEnrichedNoActionsHeuristic(
		const Problem* prob, LandmarksGraph& l, const char *arg, bool use_cache) :
	LmEnrichedHeuristic(prob, l, arg, use_cache) {
}

LmEnrichedNoActionsHeuristic::~LmEnrichedNoActionsHeuristic() {

}

int LmEnrichedNoActionsHeuristic::compute_heuristic(const State& state) {
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

	int ret = h->get_heuristic();

	int ret_act = 0;
    ActionLandmarkSet &unused_alm = lm_status_manager.get_unused_action_landmarks(*en_state);
//	int num_act = unused_alm.size();
    ActionLandmarkSet::iterator it;
    for ( it=unused_alm.begin() ; it != unused_alm.end(); it++ ) {
		ret_act += (int) (*it)->get_cost();
	}

//	cout << "------------->" << ret << " plus " << ret_act << " from " << num_act << " actions" << endl;
	return ret + ret_act;
}



void LmEnrichedNoActionsHeuristic::build_enriched_operators(vector<Operator*>& en_operators, bool create_additional_operators) {
	LmEnrichedHeuristic::build_enriched_operators(en_operators, create_additional_operators);

	// Going over the actions landmarks and setting the cost to 0
	cout << "Printing the Action Landmarks" << endl;
    const set<const Operator*>& lmops = lgraph.get_action_landmarks();
    set<const Operator*>::iterator it;
    for ( it=lmops.begin() ; it != lmops.end(); it++ ) {
    	int ind = (*it)->get_index();
    	cout << "Action Landmark with index " << ind << endl;
    	en_operators[ind]->set_double_cost(0.0);
    	(*it)->dump();
    	en_operators[ind]->dump();
	}
}
/* TODO: Take only the landmarks that are not achieved by the action landmarks */
void LmEnrichedNoActionsHeuristic::set_needed_landmarks() {

	cout << "Removing landmarks that are achieved by some action landmark." << endl;

    const set<const Operator*>& lmops = lgraph.get_action_landmarks();
    set<const Operator*>::iterator it;
    for ( it=lmops.begin() ; it != lmops.end(); it++ ) {
		(*it)->dump();

    	vector<PrePost> pre = (*it)->get_pre_post();
    	for (int i = 0; i < pre.size(); i++) {
    		pair<int, int> lm = make_pair(pre[i].var,pre[i].post);
    		if (lgraph.landmark_exists(lm)) {
    			cout << "Removing landmark " << lm.first << ": " << lm.second << endl;
    			(*it)->dump();

    			lgraph.rm_landmark(lm);
    		}
    	}
	}
	LmEnrichedHeuristic::set_needed_landmarks();
}

