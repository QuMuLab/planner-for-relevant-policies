#ifndef LM_ENRICHED_HEURISTIC_H
#define LM_ENRICHED_HEURISTIC_H

#include <string>

#include "state.h"
#include "heuristic.h"
#include "landmarks/landmarks_graph.h"
#include "landmarks/landmark_status_manager.h"
#include "problem.h"
#include "structural_patterns/SP_heuristic.h"
#include "fd_heuristic.h"

class LmEnrichedHeuristic : public Heuristic {
    friend class PartialBestFirstSearchEngine;

    Problem* en_prob;
//    vector<LandmarkNode*> en_landmarks;
protected:
    LandmarksGraph& lgraph;
    LandmarkStatusManager lm_status_manager;
	const Problem* original_problem;
    Heuristic* h;
    State* en_state;
    state_var_t* en_state_vars;

    virtual int compute_heuristic(const State& state);
    virtual void initialize();

    virtual void update_enriched_state(const State& state);
	virtual void build_enriched_operators(vector<Operator*> &ops, bool create_additional_operators);
	virtual void build_enriched_prepost(const Operator* op, vector<PrePost>& pre);
	virtual void set_needed_landmarks();

	virtual void build_enriched_variables(vector<string> &en_variable_name,vector<int> &en_variable_domain);
	virtual State* build_enriched_initial();
	virtual void build_enriched_goal(vector<pair<int, int> >& en_goal);

public:
	LmEnrichedHeuristic(LandmarksGraph& l,const char *arg, bool use_cache=false);
	LmEnrichedHeuristic(const Problem* prob, LandmarksGraph& l,const char *arg, bool use_cache=false);
    ~LmEnrichedHeuristic();

    virtual bool reach_state(const State& parent_state, const Operator &op, const State& state);
    virtual void reset();
//	virtual void print_statistics() const;

private:
	const char *h_arg;

	Operator* build_enriched_operator(const Operator* op);
	void create_remove_landmarks_operators(vector<Operator*> &en_operators);
	void build_enriched_axioms(vector<Operator> &en_operators);

	//Problem
	Problem* build_enriched_problem(bool is_HHH, bool create_additional_operators);
//	void build_dtgs(vector<int> en_variable_domain);
//	void init_en_landmarks();
	bool prev_subseteq(vector<Prevail> prv1, vector<Prevail> prv2);


};

#endif
