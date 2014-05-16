#ifndef OPERATOR_H
#define OPERATOR_H

#include <cstdlib>
#include <cassert>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#include "globals.h"
#include "state.h"
#include "policy-repair/partial_state.h"

/****************************************************************
 * HAZ:
 *   I realize there is a lot of duplication here, but I'd
 *   rather not start to try and define State and PartialState
 *   in terms of one another to avoid the overloading.
 * 
 ****************************************************************/

struct Prevail {
    int var;
    int prev;
    Prevail(std::istream &in);
    Prevail(int v, int p) : var(v), prev(p) {}

    bool is_applicable(const State &state) const {
        assert(var >= 0 && var < g_variable_name.size());
        assert(prev >= 0 && prev < g_variable_domain[var]);
        
        if (-1 == prev) {
            cout << "\n\nError: You probably tried progressing a partial state that has underspecified variables for the conditional effects.\n" << endl;
            exit(1);
        }
        
        return state[var] == prev;
    }
    
    bool is_applicable(const PartialState &state) const {
        assert(var >= 0 && var < g_variable_name.size());
        assert(prev >= 0 && prev < g_variable_domain[var]);
        return state[var] == prev;
    }

    bool operator==(const Prevail &other) const {
        return var == other.var && prev == other.prev;
    }

    bool operator!=(const Prevail &other) const {
        return !(*this == other);
    }

    void dump() const;
};

struct PrePost {
    int var;
    int pre, post;
    std::vector<Prevail> cond;
    PrePost() {} // Needed for axiom file-reading constructor, unfortunately.
    PrePost(std::istream &in);
    PrePost(int v, int pr, int po, const std::vector<Prevail> &co)
        : var(v), pre(pr), post(po), cond(co) {}

    bool is_applicable(const State &state) const {
        assert(var >= 0 && var < g_variable_name.size());
        assert(pre == -1 || (pre >= 0 && pre < g_variable_domain[var]));
        return pre == -1 || state[var] == pre;
    }
    
    bool is_applicable(const PartialState &state) const {
        assert(var >= 0 && var < g_variable_name.size());
        assert(pre == -1 || (pre >= 0 && pre < g_variable_domain[var]));
        return pre == -1 || state[var] == pre;
    }

    bool does_fire(const State &state) const {
        for (int i = 0; i < cond.size(); i++)
            if (!cond[i].is_applicable(state))
                return false;
        return true;
    }
    
    bool does_fire(const PartialState &state) const {
        for (int i = 0; i < cond.size(); i++)
            if (!cond[i].is_applicable(state))
                return false;
        return true;
    }

    bool has_conditional_effect() const {
        return cond.size() > 0;
    }

    void dump() const;
};

class Operator {
    bool is_an_axiom;
    std::vector<Prevail> prevail;      // var, val
    std::vector<PrePost> pre_post;     // var, old-val, new-val, effect conditions
    std::string name;
    std::string nondet_name;
    int cost;

    mutable bool marked; // Used for short-term marking of preferred operators
public:
    Operator(std::istream &in, bool is_axiom);
    void dump() const;
    std::string get_name() const {return name; }
    std::string get_nondet_name() const {return nondet_name; }
    
    int nondet_index;
    PartialState * all_fire_context;

    bool is_axiom() const {return is_an_axiom; }

    const std::vector<Prevail> &get_prevail() const {return prevail; }
    const std::vector<PrePost> &get_pre_post() const {return pre_post; }

    bool is_applicable(const State &state) const {
        for (int i = 0; i < prevail.size(); i++)
            if (!prevail[i].is_applicable(state))
                return false;
        for (int i = 0; i < pre_post.size(); i++)
            if (!pre_post[i].is_applicable(state))
                return false;
        return true;
    }
    
    bool is_applicable(const PartialState &state) const {
        for (int i = 0; i < prevail.size(); i++)
            if (!prevail[i].is_applicable(state))
                return false;
        for (int i = 0; i < pre_post.size(); i++)
            if (!pre_post[i].is_applicable(state))
                return false;
        return true;
    }

    bool has_conditional_effect() const {
        for (int i = 0; i < pre_post.size(); i++)
            if (pre_post[i].has_conditional_effect())
                return true;
        return false;
    }

    bool is_marked() const {
        return marked;
    }
    void mark() const {
        marked = true;
    }
    void unmark() const {
        marked = false;
    }

    mutable bool marker1, marker2; // HACK! HACK!

    int get_cost() const {return cost; }
};

#endif
