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

string RegressionStep::get_op_name() {
    if (is_goal)
        return "goal";
    else
        return op->get_name();
}

list<RegressionStep *> perform_regression(const SearchEngine::Plan &plan, vector<pair<int, int> > goal, int distance, bool create_goal) {
    
    list<RegressionStep *> reg_steps;
    State *s = new State(*g_initial_state);
    
    for (int i = 0; i < g_variable_name.size(); i++) {
        (*s)[i] = state_var_t(-1);
    }
    
    for (int i = 0; i < goal.size(); i++) {
        (*s)[goal[i].first] = state_var_t(goal[i].second);
    }
    
    reg_steps.push_back(new RegressionStep(s, distance));
    
    for (int i = plan.size() - 1; i >= 0; i--) {
        reg_steps.push_back(new RegressionStep(*plan[i], new State(*(reg_steps.back()->state), *plan[i], false), distance++));
    }
    
    if (!create_goal) {
        delete reg_steps.front();
        reg_steps.pop_front();
    }
    
    return reg_steps;
}
