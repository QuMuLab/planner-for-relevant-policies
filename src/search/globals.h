#ifndef GLOBALS_H
#define GLOBALS_H

#include "operator_cost.h"

#include <iosfwd>
#include <string>
#include <vector>
#include <map>

class AxiomEvaluator;
class CausalGraph;
class DomainTransitionGraph;
class Operator;
class Axiom;
class State;
class Heuristic;
class SuccessorGenerator;
class Timer;
class RandomNumberGenerator;
class Policy;
class DeadendAwareSuccessorGenerator;

bool test_goal(const State &state);
bool test_policy(const State &state);

void save_plan(const std::vector<const Operator *> &plan, int iter);
int calculate_plan_cost(const std::vector<const Operator *> &plan);

void read_everything(std::istream &in);
void dump_everything();

void verify_no_axioms_no_cond_effects();

void check_magic(std::istream &in, std::string magic);

bool are_mutex(const std::pair<int, int> &a, const std::pair<int, int> &b);


extern bool g_use_metric;
extern int g_min_action_cost;
extern int g_max_action_cost;

// TODO: The following five belong into a new Variable class.
extern std::vector<std::string> g_variable_name;
extern std::vector<int> g_variable_domain;
extern std::vector<std::vector<std::string> > g_fact_names;
extern std::vector<int> g_axiom_layers;
extern std::vector<int> g_default_axiom_values;

extern State *g_initial_state;
extern std::vector<std::pair<int, int> > g_goal;

extern std::vector<Operator> g_operators;
extern std::vector<Operator> g_axioms;
extern AxiomEvaluator *g_axiom_evaluator;
extern std::vector<DomainTransitionGraph *> g_transition_graphs;
extern CausalGraph *g_causal_graph;
extern Timer g_timer;
extern std::string g_plan_filename;
extern RandomNumberGenerator g_rng;

extern SuccessorGenerator *g_successor_generator_orig; // Renamed so the ops can be pruned based on deadends
extern DeadendAwareSuccessorGenerator *g_successor_generator;


extern std::map<std::string, std::vector<Operator *> > g_nondet_mapping; // Maps a non-deterministic action name to a list of ground operators
extern std::vector<std::pair<int, int> > g_matched_policy; // Contains the condition that matched when our policy recognized the state
extern int g_matched_distance; // Containts the distance to the goal for the matched policy
extern Policy *g_policy; // The policy to check while searching
extern Policy *g_regressable_ops; // The policy to check what operators are applicable
extern Policy *g_deadend_policy; // Policy that returns the set of names for nondet operators that should be avoided
extern Policy *g_deadend_states; // Policy that returns an item if the given state is a deadend
extern Policy *g_best_policy; // The best policy we've found so far
extern double g_best_policy_score; // Score for the best policy we've seen so far
extern int g_failed_open_states; // Numer of states we cannot find a plan for
extern bool g_silent_planning; // Silence the planning output
extern bool g_forgetpolicy; // Forget the policy after every simulation run
extern bool g_fullstate; // Use the full state for regression
extern bool g_plan_locally; // Plan for the expected state rather than replanning to the goal
extern bool g_plan_locally_limited; // Limit the local planning to a small number of search nodes
extern bool g_plan_with_policy; // Stop planning when the policy matches
extern bool g_partial_planlocal; // Plan locally to the partial state that would have matched our expected state
extern bool g_detect_deadends; // Decide whether or not deadends should be detected and avoided
extern bool g_generalize_deadends; // Try to find minimal sized deadends from the full state (based on relaxed reachability)
extern bool g_optimized_scd; // Do optimized strong cyclic detection
extern bool g_seeded; // Used to make sure we only seed the rng once
extern int g_num_trials; // Number of trials that should be used for the simulation
extern double g_jic_limit; // Limit for the just-in-case repairs
extern std::vector<std::pair<int, int> > g_goal_orig;
extern Heuristic *g_heuristic_for_reachability;

/* Timers */
extern Timer g_timer_regression;
extern Timer g_timer_engine_init;
extern Timer g_timer_search;
extern Timer g_timer_policy_build;
extern Timer g_timer_policy_eval;
extern Timer g_timer_policy_use;
extern Timer g_timer_jit;

#endif
