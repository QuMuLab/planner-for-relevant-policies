#ifndef LANDMARK_ENRICHED_HEURISTIC_H
#define LANDMARK_ENRICHED_HEURISTIC_H

#include <string>

#include "state.h"
#include "heuristic.h"
#include "landmarks/landmarks_graph.h"
#include "landmarks/landmark_status_manager.h"
#include "structural_patterns/SP_heuristic.h"
#include "fd_heuristic.h"
#include "problem.h"
#include "lm_graph_paths.h"

class LandmarkEnrichedHeuristic : public Heuristic {
    friend class PartialBestFirstSearchEngine;

    Problem* en_prob;
    LandmarksGraph& lgraph;
    LandmarkStatusManager lm_status_manager;
	const Problem* original_problem;
    Heuristic* h;
    State* en_state;
    state_var_t* en_state_vars;

	vector<vector<LandmarkNode*> > en_vars;
	const char *h_arg;

	void expand_path(vector<LandmarkNode*>& path, vector<vector<LandmarkNode*> >& paths);
	bool is_subpath(vector<LandmarkNode*>& path_a, vector<LandmarkNode*>& path_b);

	void create_paths_covering();
	void create_paths_all_paths();
	void create_paths_no_orderings(bool init_landmarks);

protected:
	int VARIABLESTYPE;

    virtual int compute_heuristic(const State& state);
    virtual void initialize();

    virtual void update_enriched_state(const State& state);
	virtual void build_enriched_operators(vector<Operator*> &ops, bool create_additional_operators);
	virtual void build_enriched_prepost(const Operator* op, vector<PrePost>& pre);

	virtual void build_enriched_variables(vector<string> &en_variable_name,vector<int> &en_variable_domain);
	virtual State* build_enriched_initial();
	virtual void build_enriched_goal(vector<pair<int, int> >& en_goal);


public:
	LandmarkEnrichedHeuristic(LandmarksGraph& l,const char *arg, bool use_cache=false);
	LandmarkEnrichedHeuristic(const Problem* prob, LandmarksGraph& l,const char *arg, bool use_cache=false);
    ~LandmarkEnrichedHeuristic();

    virtual bool reach_state(const State& parent_state, const Operator &op, const State& state);
    virtual void reset();
//	virtual void print_statistics() const;

    void set_variables_type(int type) {VARIABLESTYPE = type;}

private:

	Operator* build_enriched_operator(const Operator* op);
	void create_remove_landmarks_operators(vector<Operator*> &en_operators);
	void build_enriched_axioms(vector<Operator> &en_operators);

	Problem* build_enriched_problem(bool is_HHH, bool create_additional_operators);

};


#endif
