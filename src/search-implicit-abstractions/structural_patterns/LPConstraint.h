#ifndef LPCONSTRAINT_H_
#define LPCONSTRAINT_H_

using namespace std;
#include <map>
#include <vector>
#include <iostream>


struct ConstraintVar {
    int var;
    double val;
    ConstraintVar(int v, double l) : var(v), val(l) {}
    void dump(int index) { cout << val << " * x_" << var+index; }
};

class LPConstraint {

	map<int, double> c_vars;
    vector<ConstraintVar*> vars;

    double lb, ub;
    bool to_keep;
    int index;

public:
	LPConstraint();
	LPConstraint(LPConstraint* lpc, bool keep);
	LPConstraint(double l, double u, bool keep);
	virtual ~LPConstraint();

	void add_val(int var, double val);
	void finalize();
	const vector<ConstraintVar*>& get_vals() const;
	const map<int, double>& get_c_vars() const;

	double get_lb() {return lb;};
	double get_ub() {return ub;};
	bool tokeep() {return to_keep;};
	int get_index() {return index;};
	void set_index(int ind) {index = ind;};

	int get_num_vars() {return vars.size();};

    void free_mem();
    void delete_constr();
    void dump();


};

#endif /* LPCONSTRAINT_H_ */
