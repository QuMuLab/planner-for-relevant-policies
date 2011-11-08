#include "deadend.h"

void update_deadends(vector<State *> &failed_states) {
    list<PolicyItem *> de_items;
    for (int i = 0; i < failed_states.size(); i++) {
        // Get the regressable operators for the given state.
        vector<PolicyItem *> reg_items;
        g_regressable_ops->generate_applicable_items(*(failed_states[i]), reg_items);
        
        // For each operator, create a new deadend avoidance pair
        for (int j = 0; j < reg_items.size(); j++) {
            RegressableOperator *ro = (RegressableOperator*)(reg_items[j]);
            de_items.push_back(new NondetDeadend(new State(*(failed_states[i]), *(ro->op), false),
                                                     ro->op->get_nondet_name()));
        }
    }
    g_deadend_policy->update_policy(de_items);
}
