#ifndef PARTIAL_STATE_H
#define PARTIAL_STATE_H

#include <iostream>
#include <vector>

#include "../state.h"

using namespace std;

class Operator;
class State;

class PartialState {
    int *vars; // values for vars
    void _allocate();
    void _deallocate();
    void _copy_buffer_from_state(const PartialState &state);

public:
    PartialState(); // Creates a state with -1 values for everything
    PartialState(const State &state);
    PartialState(const PartialState &state);
    PartialState(const PartialState &predecessor, const Operator &op, bool progress=true, PartialState *context=NULL);
    ~PartialState();
    
    void combine_with(const PartialState &state);
    int size() const;
    
    PartialState &operator=(const PartialState &other);
    int &operator[](int index) {
        return vars[index];
    }
    int operator[](int index) const {
        return vars[index];
    }
    void dump_pddl() const;
    void dump_fdr() const;
    bool operator==(const PartialState &other) const;
    bool operator<(const PartialState &other) const;
    size_t hash() const;

};

#endif
