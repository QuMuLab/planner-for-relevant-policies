//////////
// TODO //
//////////
// - Fix the dump functions to not print undefined values
// - Move the old state functions into the state registry


#include "state.h"

#include "globals.h"
#include "utilities.h"
#include "state_registry.h"

#include <algorithm>
#include <iostream>
#include <cassert>
using namespace std;


State::State(const PackedStateBin *buffer_, const StateRegistry &registry_,
             StateID id_)
    : buffer(buffer_),
      registry(&registry_),
      id(id_) {
    assert(buffer);
    assert(id != StateID::no_state);
}

State::~State() {
}

int State::operator[](int index) const {
    return g_state_packer->get(buffer, index);
}

/*State::State(istream &in) {
    _allocate();
    check_magic(in, "begin_state");
    for (int i = 0; i < g_variable_domain.size(); i++) {
        int var;
        in >> var;
        vars[i] = var;
    }
    check_magic(in, "end_state");

    g_default_axiom_values.assign(vars, vars + g_variable_domain.size());
}

State::State() {
    _allocate();
    for (int i = 0; i < g_variable_domain.size(); i++)
        vars[i] = state_var_t(-1);
}

State::State(const State &state) {
    _allocate();
    _copy_buffer_from_state(state);
}

State::State(const State &predecessor, const Operator &op, bool progress, State *context) {
    assert(!op.is_axiom());
    _allocate();
    _copy_buffer_from_state(predecessor);
    // Update values affected by operator.
    if (progress) {
        
        for (int i = 0; i < op.get_pre_post().size(); i++) {
            const PrePost &pre_post = op.get_pre_post()[i];
            if (pre_post.does_fire(predecessor))
                vars[pre_post.var] = state_var_t(pre_post.post);
        }
        
        // HAZ: We do the prevail's as well in case we are progressing a partial state
        for (int i = 0; i < op.get_prevail().size(); i++) {
            vars[op.get_prevail()[i].var] = state_var_t(op.get_prevail()[i].prev);
        }
        
    } else {
        
        assert(NULL != context);
        
        // Get all of the pre/post conditions that fire (note: pre may be -1 here)
        for (int i = 0; i < op.get_pre_post().size(); i++) {
            if (op.get_pre_post()[i].does_fire(*context)) {
                assert((predecessor[op.get_pre_post()[i].var] == state_var_t(-1)) ||
                       (predecessor[op.get_pre_post()[i].var] == (op.get_pre_post()[i].post)));
                if (!g_fullstate || (state_var_t(op.get_pre_post()[i].pre) != state_var_t(-1))) {
                    vars[op.get_pre_post()[i].var] = state_var_t(op.get_pre_post()[i].pre);
                }
            }
        }
        
        // Assign the values from the context that are mentioned in conditions
        for (int i = 0; i < g_nondet_conditional_mask[op.nondet_index]->size(); i++) {
            int var = (*(g_nondet_conditional_mask[op.nondet_index]))[i];
            vars[var] = (*context)[var];
        }
        
        // Get all of the prevail conditions
        for (int i = 0; i < op.get_prevail().size(); i++) {
            vars[op.get_prevail()[i].var] = state_var_t(op.get_prevail()[i].prev);
        }
    }
    
    // HAZ: This is disabled since we cannot handle domains with axioms,
    //      leaving it in slows us down.
    //g_axiom_evaluator->evaluate(*this);
}

State::~State() {
    _deallocate();
}*/

void State::dump_pddl() const {
    for (int i = 0; i < g_variable_domain.size(); i++) {
        const string &fact_name = g_fact_names[i][(*this)[i]];
        if (fact_name != "<none of those>")
            cout << fact_name << endl;
    }
}

void State::dump_fdr() const {
    for (size_t i = 0; i < g_variable_domain.size(); ++i)
        cout << "  #" << i << " [" << g_variable_name[i] << "] -> "
             << (*this)[i] << endl;
}
