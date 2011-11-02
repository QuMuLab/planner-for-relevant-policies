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
    g_timer_regression.resume();
    list<RegressionStep *> reg_steps;
    State *s = new State(*g_initial_state);
    
    if (g_fullstate) {
        
        vector<State *> states;
        states.push_back(s);
        
        for (int i = 0; i < plan.size(); i++) {
            s = new State(*s, *plan[i]);
            states.push_back(s);
        }
        
        if (create_goal) {
            
            State *g = new State(*g_initial_state);
            
            for (int i = 0; i < g_variable_name.size(); i++) {
                (*g)[i] = state_var_t(-1);
            }
            
            for (int i = 0; i < goal.size(); i++) {
                (*g)[goal[i].first] = state_var_t(goal[i].second);
            }
        
            reg_steps.push_back(new RegressionStep(g, distance));
            
        } else {
            reg_steps.push_back(new RegressionStep(states.back(), distance));
        }
        
        // Remove the full goal state (we still keep the partial goal state if need be)
        states.pop_back();
        
        for (int i = plan.size() - 1; i >= 0; i--) {
            reg_steps.push_back(new RegressionStep(*plan[i], states.back(), ++distance));
            states.pop_back();
        }
        
        assert(states.empty());
        
    } else {
        for (int i = 0; i < g_variable_name.size(); i++) {
            (*s)[i] = state_var_t(-1);
        }
        
        for (int i = 0; i < goal.size(); i++) {
            (*s)[goal[i].first] = state_var_t(goal[i].second);
        }
    
        reg_steps.push_back(new RegressionStep(s, distance));
        
        for (int i = plan.size() - 1; i >= 0; i--) {
            reg_steps.push_back(new RegressionStep(*plan[i], new State(*(reg_steps.back()->state), *plan[i], false), ++distance));
        }
    }
    
    if (!create_goal) {
        delete reg_steps.front();
        reg_steps.pop_front();
    }
    g_timer_regression.stop();
    return reg_steps;
}
