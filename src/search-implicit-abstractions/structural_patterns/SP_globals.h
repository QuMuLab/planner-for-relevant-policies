#ifndef SP_GLOBALS_H
#define SP_GLOBALS_H

#include <cstdlib>

class Problem;
class State;
class Heuristic;
//class SPHeuristic;

enum {
    FORKS_ONLY,
    INVERTED_FORKS_ONLY,
    BOTH_FORKS_AND_INVERTED_FORKS,
//    FORKS_ONLY_LANDMARKS,
//    INVERTED_FORKS_ONLY_LANDMARKS,
//    BOTH_FORKS_AND_INVERTED_FORKS_LANDMARKS,
    FROM_FILE,
    OTHER
};
//extern int LP_ensemble_strategy;

enum {
    LANDMARK_VARIABLES_ONLY,
    NON_LANDMARK_VARIABLES_ONLY,
    ALL_VARIABLES,
    MIXED_LANDMARK_FORKS_NON_LANDMARK_INVERTED_FORKS,
    MIXED_NON_LANDMARK_FORKS_LANDMARK_INVERTED_FORKS
};

enum {
    GENERAL,
    UNIFORM,
    INITIAL_OPTIMAL
// ,EVERY_N_NODES_OPTIMAL
};
extern int LP_cost_partitioning;

enum {
    FORK,
    INVERTED_FORK,
    PATTERN
};

// Singletons
enum {
    NECESSARY,
    BY_DEFINITION,
    COMPENSATE_FOR_DOMAIN_DECOMPOSITION
};

enum {
    VARIABLE_PER_LANDMARK,
    VARIABLE_PER_LANDMARK_NO_INIT,
    ALL_LANDMARK_PATHS_VARIABLES,
    LANDMARK_PATHS_COVERING_VARIABLES,
    ADDITIVE_ACTION_LANDMARKS,		// Old version (new version not implemented yet)
    GENERAL_VARIABLES,             	// Old version
    SINGLE_GOAL
};

//extern int SIZEOFPATTERNLIMIT;
//extern int PERCENTAGEOFENSEMBLE;

//extern int STATISTICS;
extern int LP_INFINITY;
extern int MAX_LP_SIZE;
extern double LP_MAX_TIME_BOUND;

extern const char* groups_filename;
//extern int EVERY_N_SIZE;

extern int MAX_NUM_PATHS;
#define IFORKDOMBOUND 3

int compare (const void * a, const void * b);

Heuristic *build_sp_heuristic(const char *arg, Problem* prob, const State* state = NULL);
Heuristic *build_fd_heuristic(const char *arg, Problem* prob);
Heuristic *build_lm_enriched_heuristic(const char *arg, Problem* prob, int noactions);
int get_sp_strategy(const char *arg);


#endif
