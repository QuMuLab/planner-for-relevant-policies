#include "regression.h"

void RegressionStep::dump() const {
    cout << "Regression Step (" << distance << ")" << endl;
    if (!is_goal) {
        cout << " -{ Operator }-" << endl;
        op->dump();
    } else {
        cout << " -{ Goal }-" << endl;
    }
    cout << "\n -{ State }-" << endl;
    state->dump();
    cout << "" << endl;
}

vector<RegressionStep> perform_regression(const SearchEngine::Plan &plan, vector<pair<int, int> > goal) {
    
    vector<RegressionStep> reg_steps;
    int distance = 1;
    State *s = new State(*g_initial_state);
    
    for (int i = 0; i < g_variable_name.size(); i++) {
        (*s)[i] = state_var_t(-1);
    }
    
    for (int i = 0; i < goal.size(); i++) {
        (*s)[goal[i].first] = state_var_t(goal[i].second);
    }
    
    reg_steps.push_back(RegressionStep(s, distance));
    
    for (int i = plan.size() - 1; i >= 0; i--) {
        reg_steps.push_back(RegressionStep(*plan[i], new State(*(reg_steps.back().state), *plan[i], false), distance++));
    }
    
    return reg_steps;
}
