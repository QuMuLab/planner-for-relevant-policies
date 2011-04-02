#include "solution.h"
#include "SP_globals.h"

Solution::Solution() {

}

Solution::~Solution() {
}


void Solution::set_solution(vector<double>& s){
	sol.clear();
	for (int i=0;i<s.size();i++) {
		sol[i] = s[i];
	}
}

void Solution::set_solution(const double* s, int n_vars){
	sol.clear();
	for (int i=0;i<n_vars;i++) {
		sol[i] = s[i];
	}
}

double Solution::get_value(int var) {
	if (sol.find(var) == sol.end()) {
		cout<< "--------->No value found for " << var << endl;
		return LP_INFINITY;
	}

	return sol[var];
}

void Solution::set_value(int var, double val) {
	sol[var] = val;
}

void Solution::remove_var(int var) {
	sol.erase(sol.find(var));
}

void Solution::clear_solution(){
	sol.clear();
}

void Solution::dump(){
	for(hash_map<int, double >::iterator it = sol.begin(); it != sol.end(); it++){
		cout << "x_" << (*it).first << " = " << (*it).second << endl;
	}
}

int Solution::get_size(){
	return sol.size();
}

