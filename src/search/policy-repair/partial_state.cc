#include "partial_state.h"

#include "../axioms.h"
#include "../globals.h"
#include "../operator.h"
#include "../utilities.h"

#include <algorithm>
#include <iostream>
#include <cassert>
using namespace std;

void PartialState::_allocate() {
    vars = new int[g_variable_domain.size()];
}

void PartialState::_deallocate() {
    delete[] vars;
}

void PartialState::_copy_buffer_from_state(const PartialState &state) {
    for (int i = 0; i < g_variable_domain.size(); i++)
        vars[i] = state.vars[i];
}

PartialState & PartialState::operator=(const PartialState &other) {
    if (this != &other) {
        _allocate();
        _copy_buffer_from_state(other);
    }
    return *this;
}

PartialState::PartialState() {
    _allocate();
    for (int i = 0; i < g_variable_domain.size(); i++)
        vars[i] = -1;
}

PartialState::PartialState(const StateInterface &state) {
	_allocate();
	for (int i = 0; i < g_variable_domain.size(); i++)
		vars[i] = state[i];
}

PartialState::PartialState(const PartialState &state) {
    _allocate();
    _copy_buffer_from_state(state);
}

PartialState::PartialState(const PartialState &predecessor, const Operator &op, bool progress, PartialState *context) {
    assert(!op.is_axiom());
    _allocate();
    _copy_buffer_from_state(predecessor);
    // Update values affected by operator.
    if (progress) {
        
        for (int i = 0; i < op.get_pre_post().size(); i++) {
            const PrePost &pre_post = op.get_pre_post()[i];
            if (pre_post.does_fire(predecessor))
                vars[pre_post.var] = int(pre_post.post);
        }
        
        // HAZ: We do the prevail's as well in case we are progressing a partial state
        for (int i = 0; i < op.get_prevail().size(); i++) {
            vars[op.get_prevail()[i].var] = int(op.get_prevail()[i].prev);
        }
        
    } else {
        
        assert(NULL != context);
        
        // Get all of the pre/post conditions that fire (note: pre may be -1 here)
        for (int i = 0; i < op.get_pre_post().size(); i++) {
            if (op.get_pre_post()[i].does_fire(*context)) {
                assert((predecessor[op.get_pre_post()[i].var] == -1) ||
                       (predecessor[op.get_pre_post()[i].var] == (op.get_pre_post()[i].post)));
                if (!g_fullstate || (op.get_pre_post()[i].pre != -1)) {
                    vars[op.get_pre_post()[i].var] = op.get_pre_post()[i].pre;
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
            vars[op.get_prevail()[i].var] = int(op.get_prevail()[i].prev);
        }
    }
    
    // HAZ: This is disabled since we cannot handle domains with axioms,
    //      leaving it in slows us down.
    //g_axiom_evaluator->evaluate(*this);
}

PartialState::~PartialState() {
    _deallocate();
}

void PartialState::combine_with(const PartialState &other) {
    for (int i = 0; i < g_variable_domain.size(); i++) {
        assert((vars[i] == -1) || (other[i] == -1) || (vars[i] == other[i]));
        if (other[i] != -1)
            vars[i] = other[i];
    }
}

int PartialState::size() const {
    int count = 0;
    for (int i = 0; i < g_variable_domain.size(); i++) {
        if (vars[i] != -1)
            count++;
    }
    return count;
}

void PartialState::dump_pddl() const {
    for (int i = 0; i < g_variable_domain.size(); i++) {
        if (-1 != vars[i]) {
            const string &fact_name = g_fact_names[i][vars[i]];
            if (fact_name != "<none of those>")
                cout << fact_name << endl;
            else
                cout << "[" << g_variable_name[i] << "] None of those." << endl;
        }
    }
}

void PartialState::dump_fdr() const {
    // We cast the values to int since we'd get bad output otherwise
    // if state_var_t == char.
    for (int i = 0; i < g_variable_domain.size(); i++) {
        if (-1 != vars[i]) {
            cout << "  #" << i << " [" << g_variable_name[i] << "] -> "
                 << vars[i] << endl;
        }
    }
}

bool PartialState::operator==(const PartialState &other) const {
    int size = g_variable_domain.size();
    return ::equal(vars, vars + size, other.vars);
}

bool PartialState::operator<(const PartialState &other) const {
    int size = g_variable_domain.size();
    return ::lexicographical_compare(vars, vars + size,
                                     other.vars, other.vars + size);
}

size_t PartialState::hash() const {
    return ::hash_number_sequence(vars, g_variable_domain.size());
}
