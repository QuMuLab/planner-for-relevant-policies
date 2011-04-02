#ifndef LP_SOLUTION_H_
#define LP_SOLUTION_H_
#include "../globals.h"
using namespace std;
#include <vector>
#include <iostream>
#include <ext/hash_map>

using namespace __gnu_cxx;


class Solution {
private:
//	vector<double> sol;
	hash_map<int, double > sol;

public:
	Solution();
	virtual ~Solution();
	void set_solution(vector<double>& s);
	void set_solution(const double* s, int n_vars);
	double get_value(int var);
	void set_value(int var, double val);
	void remove_var(int var);
	void clear_solution();
	void dump();
	int get_size();
};

#endif /* LP_SOLUTION_H_ */
