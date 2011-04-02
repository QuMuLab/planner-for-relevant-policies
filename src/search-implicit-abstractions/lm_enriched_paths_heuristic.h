#ifndef LM_ENRICHED_PATHS_HEURISTIC_H
#define LM_ENRICHED_PATHS_HEURISTIC_H


#include "landmarks/landmarks_graph.h"
#include "landmarks/landmark_status_manager.h"
#include "problem.h"
#include "lm_enriched_heuristic.h"

class LmEnrichedPathsHeuristic : public LmEnrichedHeuristic {
	vector<vector<LandmarkNode*> > en_vars;

	void expand_path(vector<LandmarkNode*>& path, vector<vector<LandmarkNode*> >& paths);
	bool is_subpath(vector<LandmarkNode*>& path_a, vector<LandmarkNode*>& path_b);

	void create_paths_covering();
	void create_paths_all_paths();
	void create_paths_no_orderings();

protected:
	virtual void set_needed_landmarks();
	virtual void update_enriched_state(const State& state);
	virtual void build_enriched_variables(
			vector<string> &en_variable_name, vector<int> &en_variable_domain);

	virtual State* build_enriched_initial();
	virtual void build_enriched_goal(vector<pair<int, int> >& en_goal);
	virtual void build_enriched_prepost(const Operator* op, vector<PrePost>& pre);
public:
	LmEnrichedPathsHeuristic(LandmarksGraph& l,const char *arg, bool use_cache=false);
	LmEnrichedPathsHeuristic(const Problem* prob, LandmarksGraph& l,const char *arg, bool use_cache=false);
    ~LmEnrichedPathsHeuristic();

};

#endif
