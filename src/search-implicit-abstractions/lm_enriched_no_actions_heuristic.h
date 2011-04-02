#ifndef LM_ENRICHED_NO_ACTIONS_HEURISTIC_H
#define LM_ENRICHED_NO_ACTIONS_HEURISTIC_H


#include "landmarks/landmarks_graph.h"
#include "landmarks/landmark_status_manager.h"
#include "problem.h"
#include "lm_enriched_heuristic.h"

class LmEnrichedNoActionsHeuristic : public LmEnrichedHeuristic {
protected:
	virtual int compute_heuristic(const State& state);
	virtual void build_enriched_operators(vector<Operator*> &ops, bool create_additional_operators);
	virtual void set_needed_landmarks();
public:
	LmEnrichedNoActionsHeuristic(LandmarksGraph& l,const char *arg, bool use_cache=false);
	LmEnrichedNoActionsHeuristic(const Problem* prob, LandmarksGraph& l,const char *arg, bool use_cache=false);
    ~LmEnrichedNoActionsHeuristic();

};

#endif
