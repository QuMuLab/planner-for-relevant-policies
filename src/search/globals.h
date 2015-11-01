#ifndef GLOBALS_H
#define GLOBALS_H

#include <iosfwd>
#include <string>
#include <vector>
#include <map>

class Axiom;
class AxiomEvaluator;
class CausalGraph;
class DomainTransitionGraph;
class IntPacker;
class LegacyCausalGraph;
class Operator;
class RandomNumberGenerator;
class State;
class PartialState;
class Heuristic;
class SuccessorGenerator;
class Timer;
class StateRegistry;
class RandomNumberGenerator;
class Policy;
class DeadendAwareSuccessorGenerator;
class RegressionStep;
class NondetDeadend;

bool test_goal(const State &state);
bool test_policy(const State &state);

void save_plan(const std::vector<const Operator *> &plan, int iter);
int calculate_plan_cost(const std::vector<const Operator *> &plan);

void read_everything(std::istream &in);
void dump_everything();

bool has_axioms();
void verify_no_axioms();
int get_first_cond_effects_op_id();
bool has_cond_effects();
void verify_no_cond_effects();
void verify_no_axioms_no_cond_effects();

void check_magic(std::istream &in, std::string magic);

bool are_mutex(const std::pair<int, int> &a, const std::pair<int, int> &b);

struct DeadendTuple {
    PartialState *de_state;
    PartialState *prev_state;
    const Operator *prev_op;

    DeadendTuple(PartialState *ds, PartialState *ps, const Operator *op) : de_state(ds), prev_state(ps), prev_op(op) {}
    ~DeadendTuple();
};

extern bool g_use_metric;
extern int g_min_action_cost;
extern int g_max_action_cost;

// TODO: The following five belong into a new Variable class.
extern std::vector<std::string> g_variable_name;
extern std::vector<int> g_variable_domain;
extern std::vector<std::vector<std::string> > g_fact_names;
extern std::vector<int> g_axiom_layers;
extern std::vector<int> g_default_axiom_values;

extern IntPacker *g_state_packer;
// This vector holds the initial values *before* the axioms have been evaluated.
// Use the state registry to obtain the real initial state.
extern std::vector<int> g_initial_state_data;
// TODO The following function returns the initial state that is registered
//      in g_state_registry. This is only a short-term solution. In the
//      medium term, we should get rid of the global registry.
extern const State &g_initial_state();
extern std::vector<std::pair<int, int> > g_goal;

extern std::vector<Operator> g_operators;
extern std::vector<Operator> g_axioms;
extern AxiomEvaluator *g_axiom_evaluator;
extern std::vector<DomainTransitionGraph *> g_transition_graphs;
extern CausalGraph *g_causal_graph;
extern LegacyCausalGraph *g_legacy_causal_graph;
extern Timer g_timer;
extern std::string g_plan_filename;
extern RandomNumberGenerator g_rng;
// Only one global object for now. Could later be changed to use one instance
// for each problem in this case the method State::get_id would also have to be
// changed.
extern StateRegistry *g_state_registry;

extern SuccessorGenerator *g_successor_generator_orig; // Renamed so the ops can be pruned based on deadends
extern DeadendAwareSuccessorGenerator *g_successor_generator;


extern std::map<std::string, int> g_nondet_index_mapping; // Maps a non-deterministic action name to its id
extern std::vector<std::vector<Operator *> *> g_nondet_mapping; // Maps a non-deterministic action id to a list of ground operators
extern std::vector<std::vector<int> *> g_nondet_conditional_mask; // Maps a non-deterministic action id to the variables that must be defined when doing context-sensitive regression
extern RegressionStep *g_matched_policy; // Contains the condition that matched when our policy recognized the state
extern int g_matched_distance; // Containts the distance to the goal for the matched policy
extern Policy *g_policy; // The policy to check while searching
extern Policy *g_regressable_ops; // The policy to check what operators are applicable
extern Policy *g_regressable_cond_ops; // The policy to check what operators with conditional effects are applicable
extern Policy *g_deadend_policy; // Policy that returns the set of names for nondet operators that should be avoided
extern Policy *g_deadend_states; // Policy that returns an item if the given state is a deadend
extern Policy *g_temporary_deadends; // Policy that stores deadends as we find them online (to avoid repeated ones)
extern Policy *g_best_policy; // The best policy we've found so far
extern std::vector< DeadendTuple * > g_found_deadends; // Vector of deadends / contexts found while planning
extern double g_best_policy_score; // Score for the best policy we've seen so far
extern int g_failed_open_states; // Numer of states we cannot find a plan for
extern bool g_updated_deadends; // True if updating the policy created new deadends
extern bool g_replan_detected_deadends; // True if the weak planning procedure created a new deadend
extern bool g_silent_planning; // Silence the planning output
extern bool g_forgetpolicy; // Forget the policy after every simulation run
extern bool g_replan_during_simulation; // True if we want to allow the system to replan
extern bool g_fullstate; // Use the full state for regression
extern bool g_plan_locally; // Plan for the expected state rather than replanning to the goal
extern bool g_plan_locally_limited; // Limit the local planning to a small number of search nodes
extern bool g_limit_states; // Used to limit the search when replanning for a local goal
extern int g_limit_states_max; // Maximum number of states to expand in the subsequent search
extern bool g_force_limit_states; // Forces the search to stop based on the g_limit_states_max
extern bool g_plan_with_policy; // Stop planning when the policy matches
extern bool g_partial_planlocal; // Plan locally to the partial state that would have matched our expected state
extern bool g_detect_deadends; // Decide whether or not deadends should be detected and avoided
extern bool g_check_with_forbidden; // We set this when a strong cyclic policy is failed to be found without using forbidden ops in the heuristic
extern bool g_generalize_deadends; // Try to find minimal sized deadends from the full state (based on relaxed reachability)
extern bool g_record_online_deadends; // Record the deadends as they occur online, and add them to the deadend policy after solving
extern bool g_sample_for_depth1_deadends; // Analyze the non-deterministic alternate states from the generated weak plans for deadends
extern bool g_combine_deadends; // Combine FSAP conditions for a new deadend when there are no applicable actions
extern bool g_repeat_fsap_backwards; // Keep making FSAPs as long as states where they hold have no applicable actions
extern bool g_regress_only_relevant_deadends; // Only regresses a deadend for an FSAP if the action triggers the deadend
extern int g_combined_count; // Number of times a deadend was generated from combining FSAPs
extern int g_repeat_fsap_count; // Number of times we applied the repeated FSAP technique
extern bool g_repeat_strengthening; // Continue to strengthen pairs back to the initial state.
extern bool g_optimized_scd; // Do optimized strong cyclic detection
extern bool g_final_fsap_free_round; // Do a final JIC pass with deadends disabled
extern bool g_seeded; // Used to make sure we only seed the rng once
extern int g_trial_depth; // Used to limit the number of simulation steps
extern int g_num_trials; // Number of trials that should be used for the simulation
extern double g_jic_limit; // Limit for the just-in-case repairs
extern std::vector<std::pair<int, int> > g_goal_orig;
extern Heuristic *g_heuristic_for_reachability;
extern int g_dump_policy; // Whether or not we should dump the policy
extern int g_monotonicity_violations; // Count on the number of times we need to add a deadend because of a bad policy loop
extern int g_num_regsteps; // Used to give each regstep an id based on when it was created
extern int g_num_epochs; // Forced number of times to run the jic loop

extern bool g_optimize_final_policy; // Only keep the final pairs and FSAPs that are needed
extern bool g_record_relevant_pairs; // If true, used pairs will be kept

extern bool g_debug; // Flag for debugging parts of the code
extern int g_debug_count; // Index that allows to locate spots in the output

extern bool g_safetybelt_optimized_scd; // Gradually disable the optimized SCD setting when it proves useless

/* Timers */
extern Timer g_timer_regression;
extern Timer g_timer_simulator;
extern Timer g_timer_engine_init;
extern Timer g_timer_search;
extern Timer g_timer_policy_build;
extern Timer g_timer_policy_eval;
extern Timer g_timer_policy_use;
extern Timer g_timer_jit;

#endif
