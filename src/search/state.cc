#include "state.h"

#include "axioms.h"
#include "globals.h"
#include "operator.h"
#include "utilities.h"

#include <algorithm>
#include <iostream>
#include <cassert>
using namespace std;

void State::_allocate() {
    borrowed_buffer = false;
    vars = new state_var_t[g_variable_domain.size()];
}

void State::_deallocate() {
    if (!borrowed_buffer)
        delete[] vars;
}

void State::_copy_buffer_from_state(const State &state) {
    // TODO: Profile if memcpy could speed this up significantly,
    //       e.g. if we do blind A* search.
    for (int i = 0; i < g_variable_domain.size(); i++)
        vars[i] = state_var_t(state.vars[i]);
}

State & State::operator=(const State &other) {
    if (this != &other) {
        if (borrowed_buffer)
            _allocate();
        _copy_buffer_from_state(other);
    }
    return *this;
}

State::State(istream &in) {
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

State::State(const State &predecessor, const Operator &op, bool progress) {
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
        // Make sure there are no conditional effects
        assert(!op.has_conditional_effect());
        
        // Get all of the pre/post conditions (note: pre may be -1 here)
        for (int i = 0; i < op.get_pre_post().size(); i++) {
            if (!g_fullstate || (state_var_t(op.get_pre_post()[i].pre) != state_var_t(-1)))
                vars[op.get_pre_post()[i].var] = state_var_t(op.get_pre_post()[i].pre);
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
}

void State::dump() const {
    // We cast the values to int since we'd get bad output otherwise
    // if state_var_t == char.
    for (int i = 0; i < g_variable_domain.size(); i++) {
        if (state_var_t(-1) != vars[i]) {
            cout << "  " << g_variable_name[i] << ": "
                 << static_cast<int>(vars[i]) << endl;
        }
    }
}

bool State::operator==(const State &other) const {
    int size = g_variable_domain.size();
    return ::equal(vars, vars + size, other.vars);
}

bool State::operator<(const State &other) const {
    int size = g_variable_domain.size();
    return ::lexicographical_compare(vars, vars + size,
                                     other.vars, other.vars + size);
}

size_t State::hash() const {
    return ::hash_number_sequence(vars, g_variable_domain.size());
}
