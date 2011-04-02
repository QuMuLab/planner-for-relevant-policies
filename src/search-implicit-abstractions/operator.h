#ifndef OPERATOR_H
#define OPERATOR_H

#include <cassert>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <algorithm>

#include "globals.h"
#include "state.h"

struct Prevail {
    int var;
    int prev;
    Prevail(std::istream &in);
    Prevail(int v, int p) : var(v), prev(p) {}

    bool is_applicable(const State &state) const {
	assert(var >= 0 && var < g_variable_name.size());
	assert(prev >= 0 && prev < g_variable_domain[var]);
	return state[var] == prev;
    }

    void dump() const;
    // Added by Michael
    bool operator==(const Prevail &other) const {
    	return (var == other.var && prev == other.prev);
    }
    bool operator!=(const Prevail &other) const {
    	return !(*this == other);
    }
    bool operator<(const Prevail &other) const {
    	return (var < other.var || (var == other.var && prev < other.prev));
    }
    void dump_SAS(ofstream& os) const {
    	os << var << " " << prev << endl;
    }
};

struct PrePost {
    int var;
    int pre, post;
    std::vector<Prevail> cond;
    PrePost() {} // Needed for axiom file-reading constructor, unfortunately.
    PrePost(std::istream &in);
    PrePost(int v, int pr, int po, const std::vector<Prevail> &co)
	: var(v), pre(pr), post(po), cond(co) {
    	  // Michael: sorting the condition vector.
    	  ::sort(cond.begin(), cond.end());
    }

    bool is_applicable(const State &state) const {
	assert(var >= 0 && var < g_variable_name.size());
	assert(pre == -1 || (pre >= 0 && pre < g_variable_domain[var]));
	return pre == -1 || state[var] == pre;
    }

    bool does_fire(const State &state) const {
	for(int i = 0; i < cond.size(); i++)
	    if(!cond[i].is_applicable(state))
		return false;
	return true;
    }

    void dump() const;
    // Added by Michael
    bool operator==(PrePost &other) {
    	if (cond.size() != other.cond.size()) return false;
    	if (var != other.var || pre != other.pre || post != other.post) return false;
//    	::sort(cond.begin(), cond.end());
//    	::sort(other.cond.begin(), other.cond.end());
    	for (int i = 0; i < cond.size(); i++)
    		if (cond[i] != other.cond[i]) return false;

    	return true;
    }
    bool operator<(const PrePost &other) const {
    	//TODO: include condition in the check
    	return (var < other.var || (var == other.var && post < other.post)
    			|| (var == other.var && post == other.post && pre < other.pre));
    }

    void dump_SAS(ofstream& os) const {
      	os << cond.size() << endl;
    	for(int i = 0; i < cond.size(); i++){
    		cond[i].dump_SAS(os);
    	}
    	os << var << " " << pre << " " << post << endl;
    }


};

class Operator {
    bool is_an_axiom;
    std::vector<Prevail> prevail;      // var, val
    std::vector<PrePost> pre_post;     // var, old-val, new-val, effect conditions
    std::string name;
    int cost;
    int index;          				// Added by Michael
    double d_cost;       				// Added by Michael

    mutable bool marked; // Used for short-term marking of preferred operators
public:
    Operator(std::istream &in, bool is_axiom);
    void dump() const;
    std::string get_name() const {return name;}

    bool is_axiom() const {return is_an_axiom;}

    const std::vector<Prevail> &get_prevail() const {return prevail;}
    const std::vector<PrePost> &get_pre_post() const {return pre_post;}

    bool is_applicable(const State &state) const {
	for(int i = 0; i < prevail.size(); i++)
	    if(!prevail[i].is_applicable(state))
		return false;
	for(int i = 0; i < pre_post.size(); i++)
	    if(!pre_post[i].is_applicable(state))
		return false;
	return true;
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

    int get_cost() const {return cost;}

    // Added by Michael
    Operator(bool is_axiom,
    		 std::vector<Prevail> prv,
    		 std::vector<PrePost> pre,
    		 std::string nm,
    		 double c)
    {
    	marked = false;
    	is_an_axiom = is_axiom;
        prevail = prv;
        pre_post = pre;
        name = nm;
        d_cost = c;
        sort_and_remove_duplicates();
        marker1 = marker2 = false;
    }

    double get_double_cost() const {return d_cost;}
    void set_double_cost(double c) {d_cost=c;}
    int get_index() const {return index;}
    void set_index(int ind) {index = ind;}

    bool is_prevailed_by(int v) const {
    	for(int i = 0; i < prevail.size(); i++)
    		if (prevail[i].var == v) return true;
    	return false;
    }

    int get_prevail_val(int v) const {
    	for(int i = 0; i < prevail.size(); i++)
    		if (prevail[i].var == v) return prevail[i].prev;
    	return -1;
    }

    int get_pre_val(int v) const {
    	for(int i = 0; i < pre_post.size(); i++)
    		if (pre_post[i].var == v) return pre_post[i].pre;
    	return -1;
    }

    int get_post_val(int v) const {
    	for(int i = 0; i < pre_post.size(); i++)
    		if (pre_post[i].var == v) return pre_post[i].post;
    	return -1;
    }

    bool is_redundant() const {
    	for (int i=0;i<pre_post.size();i++) {
    		if (pre_post[i].pre != pre_post[i].post)
    			return false;
    	}
    	return (0==pre_post.size());
    }

    void sort_and_remove_duplicates() {
        ::sort(pre_post.begin(), pre_post.end());
    	for(int i = pre_post.size() - 1; i > 0; i--){
    		if (pre_post[i] == pre_post[i-1])
    			pre_post.erase(pre_post.begin()+i);
    	}
    }

    void dump_SAS(ofstream& os) const {
    	if (is_an_axiom) {
    		os << "begin_rule" << endl;
    		pre_post[0].dump_SAS(os);
    		os << "end_rule" << endl;
    	} else {
    		os << "begin_operator" << endl;
    	   	os << name << endl;
    	   	os << prevail.size() << endl;
        	for(int i = 0; i < prevail.size(); i++){
        		prevail[i].dump_SAS(os);
        	}
    	   	os << pre_post.size() << endl;
        	for(int i = 0; i < pre_post.size(); i++){
        		pre_post[i].dump_SAS(os);
        	}

        	if (g_use_metric)
        		os << cost << endl;
        	else
        		os << "0" << endl;

    		os << "end_operator" << endl;
    	}
    }

};

#endif
