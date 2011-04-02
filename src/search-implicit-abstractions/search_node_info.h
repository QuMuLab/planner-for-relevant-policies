#ifndef SEARCH_NODE_INFO_H
#define SEARCH_NODE_INFO_H

#include "state.h"

class SearchNodeInfo {
public:
    friend class SearchNode;
    friend class SearchSpace;

    enum NodeStatus {NEW = 0, OPEN = 1, CLOSED = 2, DEAD_END = 3};

    /*
      NodeStatus status;
      int g;
      int h;
    */

    unsigned int status: 2;

#ifdef HIGH_COST_ACTIONS
    int g:30;
    int h:31;
#else
    int g:14;
    int h:15;
#endif

    unsigned int need_eval: 1;

    const state_var_t *parent_state;
    const Operator *creating_operator;

    SearchNodeInfo()
    : status(NEW), g(-1), h(-1), need_eval(1), parent_state(0), creating_operator(0) {
    }

};

#endif
