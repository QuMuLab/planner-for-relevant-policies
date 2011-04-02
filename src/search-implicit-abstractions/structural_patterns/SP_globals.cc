#include "SP_globals.h"

#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>
#include "SP_heuristic.h"
#include "LP_heuristic.h"
#include "state_opt_heuristic.h"
//#include "offline_heuristic.h"
#include "online_heuristic.h"
#include "init_opt_heuristic.h"
#include "../fd_heuristic.h"
#include "../lm_enriched_heuristic.h"
#include "../lm_enriched_no_actions_heuristic.h"
#include "../lm_enriched_paths_heuristic.h"
#include "../landmarks/landmarks_count_heuristic.h"
#include "../landmark_enriched_heuristic.h"

using namespace std;

int MAX_LP_SIZE = 500000;
double LP_MAX_TIME_BOUND = -1;
int MAX_NUM_PATHS = 100;
const char* groups_filename = "all.groups";


Heuristic *build_lm_enriched_heuristic(const char *arg, Problem* prob, int type) {
//    LandmarksCountHeuristic lmh(false, true, false, LandmarksCountHeuristic::rpg_sasp);
    LandmarksCountHeuristic lmh(false, true, false);
	LandmarksGraph* lm_graph = g_lgraph;

//    if (g_print_lm_graph) {
//   	lm_graph->dump_enriched();
//    }

    if (type == ADDITIVE_ACTION_LANDMARKS) {
    	return new LmEnrichedNoActionsHeuristic(prob, *lm_graph, arg);
//    } else if (type == LANDMARKPATHSVARIABLES) {
//    	return new LmEnrichedPathsHeuristic(prob, *lm_graph, arg);
    } else if (type == GENERAL_VARIABLES) {
        return new LmEnrichedHeuristic(prob, *lm_graph, arg);
    } else if (type == SINGLE_GOAL) {
    	const char* filename = "singlegoal.sas";
    	cout << "Single goal task is written to "<< filename << endl
			 << "Run preprocess again and then solve." << endl;

    	if (prob == NULL)
    		prob = new Problem();  // translator causal graph

    	prob->make_single_goal();
    	prob->dump_SAS(filename);
    	exit(1);
    } else { // All other cases
    	LandmarkEnrichedHeuristic* h = new LandmarkEnrichedHeuristic(prob, *lm_graph, arg);
    	h->set_variables_type(type);
    	return h;
    }
}




Heuristic *build_fd_heuristic(const char *arg, Problem* prob) {

	if (prob == NULL)
			prob = new Problem(true);
	//prob->dump();
	for(const char *c = (arg + 1); *c != 0; c++) {
		if (*c >= '0' && *c <= '9') {
			g_abstraction_max_size = ::atoi(c);
			while (*c >= '0' && *c <= '9')
				c++;
			c--;
			if (g_abstraction_max_size < 1) {
				cerr << "error: abstraction size must be at least 1" << endl;
				exit(91);
			}
		} else if (*c == 'A') {
			c++;
			g_abstraction_nr = ::atoi(c);
			while (*c >= '0' && *c <= '9')
				c++;
			c--;
		} else if (*c == 'R') {
			c++;
			int seed = ::atoi(c);
			while (*c >= '0' && *c <= '9')
				c++;
			c--;
			cout << "random seed: " << seed << endl;
			srand(seed);
		} else if (*c == 'S') {
			const char *arg = c;
			c++;
			g_compose_strategy = *c++ - '1';
			if (g_compose_strategy < 0 || g_compose_strategy >= MAX_COMPOSE_STRATEGY) {
				cerr << "Unknown option: " << arg << endl;
				exit(93);
			}
			g_collapse_strategy = *c++ - '1';
			if (g_collapse_strategy < 0 || g_collapse_strategy >= MAX_COLLAPSE_STRATEGY) {
				cerr << "Unknown option: " << arg << endl;
				exit(92);
			}
			if (*c == '1' || *c == '2') {
				if (*c == '2')
					g_merge_and_shrink_bound_is_for_product = false;
				c++;
			}
			c--;
		} else {
			cerr << "Unknown option: " << *c << endl;
			exit(94);
		}

	}
    cout << "Composition strategy: ";
    if (g_compose_strategy == COMPOSE_LINEAR_CG_GOAL_LEVEL) {
        cout << "linear CG/GOAL, tie breaking on level (main)";
    } else if (g_compose_strategy == COMPOSE_LINEAR_CG_GOAL_RANDOM) {
        cout << "linear CG/GOAL, tie breaking random";
    } else if (g_compose_strategy == COMPOSE_LINEAR_GOAL_CG_LEVEL) {
        cout << "linear GOAL/CG, tie breaking on level";
    } else if (g_compose_strategy == COMPOSE_LINEAR_RANDOM) {
        cout << "linear random";
    } else if (g_compose_strategy == COMPOSE_DFP) {
        cout << "Draeger/Finkbeiner/Podelski";
    }
    cout << endl;
    if (g_compose_strategy == COMPOSE_DFP) {
        cerr << "DFP composition strategy not implemented." << endl;
		exit(89);
    }

    cout << "Collapsing strategy: ";
    if (g_collapse_strategy == COLLAPSE_HIGH_F_LOW_H) {
        cout << "high f/low h (main)";
    } else if (g_collapse_strategy == COLLAPSE_LOW_F_LOW_H) {
        cout << "low f/low h";
    } else if (g_collapse_strategy == COLLAPSE_HIGH_F_HIGH_H) {
        cout << "high f/high h";
    } else if (g_collapse_strategy == COLLAPSE_RANDOM) {
        cout << "random states";
    } else if (g_collapse_strategy == COLLAPSE_DFP) {
        cout << "Draeger/Finkbeiner/Podelski";
    }
    cout << endl;

	return new FinkbeinerDraegerHeuristic;
}
//class SPHeuristic;


int get_sp_strategy(const char *arg) {
	for(const char *c = arg; *c != 0; c++) {
		if(*c == 'M') 	// mixed strategy - from file
	    	return FROM_FILE;
	    if(*c == 'L')
    		return FORKS_ONLY;
	    if(*c == 'I')
    		return INVERTED_FORKS_ONLY;
	    if(*c == 'B')
    		return BOTH_FORKS_AND_INVERTED_FORKS;
	}
	cerr << "Unknown strategy option: " << *arg << endl;
	exit( 3 );
}


Heuristic *build_sp_heuristic(const char *arg, Problem* prob, const State* state) {
	cout << "Options: " << arg << endl;
	int strategy = OTHER;
	int singletons_strategy = NECESSARY;
	bool LP_heuristic = false;
	bool online_heuristic = false;
	int LP_cost_partitioning = UNIFORM;
	int SIZEOFPATTERNLIMIT = 0;
	int PERCENTAGEOFENSEMBLE = 100;
	int STATISTICS = 0;
	int selected_ensemble = ALL_VARIABLES;

	if (prob == NULL) {
		prob = new Problem();
		assert(state == NULL);
	}

	if (state == NULL) {
		state = prob->get_initial_state();
	}

	for(const char *c = arg; *c != 0; c++) {
	    if(*c == 'O') {
	    	// Michael: LP heuristics with Optimal cost partitioning by default.
	    	// In order to use uniform partitioning, use with option OU
	    	LP_heuristic = true;
	    	LP_cost_partitioning = GENERAL;
	    } else if(*c == 'X') {	// offline heuristic - cost partitioning is based on optimal for init
	    	LP_cost_partitioning = INITIAL_OPTIMAL;
	    } else if(*c == 'U') { 	// online heuristics - uniform cost partitioning
	    	LP_cost_partitioning = UNIFORM;
	    	online_heuristic = true;
	    } else if(*c == 'M') { 	// mixed strategy - from file
	    	strategy = FROM_FILE;
	    } else if(*c == 'L') {
    		strategy = FORKS_ONLY;
	    } else if(*c == 'I') {
    		strategy = INVERTED_FORKS_ONLY;
	    } else if(*c == 'B') {
    		strategy = BOTH_FORKS_AND_INVERTED_FORKS;
	    } else if(*c == 'S') {
	    	singletons_strategy = COMPENSATE_FOR_DOMAIN_DECOMPOSITION;
	    } else if(*c == 'C') {
	    	STATISTICS++;
	    } else if(*c == 'i') {
	    	prob->increase_operators_cost();
	    } else if(*c == 'D') {
	    	// dumping problem to file
	    	const char* filename = "enriched.sas";
	    	cout << "Enriched task is written to "<< filename << endl
				 << "Run preprocess again and then solve." << endl;
	    	prob->dump_SAS(filename);
	    	exit(1);
	    } else if(*c == 'A') {
	    	selected_ensemble = ALL_VARIABLES;
	    } else if(*c == 'E') {
	    	selected_ensemble = MIXED_LANDMARK_FORKS_NON_LANDMARK_INVERTED_FORKS;
	    } else if(*c == 'F') {
	    	selected_ensemble = MIXED_NON_LANDMARK_FORKS_LANDMARK_INVERTED_FORKS;
	    } else if(*c == 'N') {
	    	selected_ensemble = NON_LANDMARK_VARIABLES_ONLY;
	    } else if(*c == 'Q') {
	    	selected_ensemble = LANDMARK_VARIABLES_ONLY;
	    } else if(*c == 'P') {
	        c++;
	    	SIZEOFPATTERNLIMIT = ::atoi(c);
	        while(*c >= '0' && *c <= '9')
	        	c++;
	        c--;
	    } else if(*c == 'p') {
	        c++;
	        PERCENTAGEOFENSEMBLE = ::atoi(c);
	        while(*c >= '0' && *c <= '9')
	        	c++;
	        c--;
	    } else {
	    	cerr << "Unknown option: " << *c << endl;
	    	exit( 3 );
	    }
	}

	if (strategy == OTHER) {
		cerr << "Must select a strategy for structural pattern: " << *arg << endl;
		exit ( 3 );
	}

	SPHeuristic *l;

	if(LP_heuristic) {
//#ifdef USE_MOSEK
#ifdef USE_LP
		l = new LPHeuristic(prob);
#else
		cout << "No LP Solver defined in this version" << endl;
		exit(1);
#endif
	} else if (online_heuristic){
		l = new OnlineHeuristic(prob);
	} else {
		if (LP_cost_partitioning == UNIFORM) {
			l = new SPHeuristic(prob);
		} else if (LP_cost_partitioning == INITIAL_OPTIMAL) {
//#ifdef USE_MOSEK
#ifdef USE_LP
		l = new StateOptimalHeuristic(*state, prob);
//			l = new InitialOptimalHeuristic(prob);
#else
		cout << "No LP Solver defined in this version" << endl;
		exit(1);
#endif
		} else {
	    	cerr << "Illegal cost partitioning : " << LP_cost_partitioning << " for offline heuristic" << endl;
	    	exit( 3 );
		}
    }
   	l->set_strategy(strategy);
   	l->set_selected_ensemble_strategy(selected_ensemble);
	l->set_singletons_strategy(singletons_strategy);
	l->set_cost_partitioning_strategy(LP_cost_partitioning);
	l->set_statistics_level(STATISTICS);
	l->set_percentage_of_ensemble(PERCENTAGEOFENSEMBLE);
	l->set_minimal_size_for_non_projection_pattern(SIZEOFPATTERNLIMIT);
//    l->set_name(arg);
	return l;
}

#ifdef HIGH_COST_ACTIONS
int LP_INFINITY = 1000000000;
#else
int LP_INFINITY = 100000;
#endif

