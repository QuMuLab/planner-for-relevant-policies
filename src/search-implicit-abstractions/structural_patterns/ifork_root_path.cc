#include "ifork_root_path.h"

IforkRootPath::IforkRootPath() {
	is_borrowed_lpc = false;
	lpc = NULL;
}

IforkRootPath::IforkRootPath(int sz) {
	is_borrowed_lpc = false;
	set_num_vars(sz);
	lpc = NULL;
}

IforkRootPath::IforkRootPath(IforkRootPath* cp) {
	// Copy constructor
	is_borrowed_lpc = true;
//	cp->get_path(path);
	path = cp->get_path();
//	cp->get_first_needed_pairs(first_needed_pairs);
	first_needed_pairs = cp->get_first_needed_pairs();
	set_num_vars(cp->get_num_vars());
	for (int i =0; i < first_needed_pairs.size(); i++) {
		first_needed[first_needed_pairs[i].first] = first_needed_pairs[i].second;
	}
	set_needed_cost(cp->get_needed_cost());
	set_LP_constraint(cp->get_LP_constraint());
}


IforkRootPath::~IforkRootPath() {
	if (lpc && !is_borrowed_lpc)
		delete lpc;

}

void IforkRootPath::set_num_vars(int vars) {
	num_vars = vars;
	first_needed.assign(vars,-1);
}

int IforkRootPath::get_num_vars() {
	return num_vars;
}

int IforkRootPath::get_path_size() const {
	return path.size();
}

//void IforkRootPath::get_path(vector<Operator*>& p) const {
//	p = path;
//}

void IforkRootPath::set_path(vector<Operator*>& p) {
	path = p;
}

int IforkRootPath::get_first_needed(int v) const {
	return first_needed[v];
}

void IforkRootPath::set_first_needed(int v, int val) {
	first_needed[v] = val;
}

void IforkRootPath::set_first_needed_pairs(){
	first_needed_pairs.clear();
	for (int v=0; v< num_vars; v++) {
		if (-1 != first_needed[v]) {
			pair<int, int> needed;
			needed.first = v;
			needed.second = first_needed[v];
			first_needed_pairs.push_back(needed);
		}
	}
}

//void IforkRootPath::get_first_needed_pairs(vector<pair<int,int> >& pairs){
//	pairs = first_needed_pairs;
//}

double IforkRootPath::get_path_cost() const {
	double c = 0.0;
	for (int i = 0; i < path.size(); i++) {
		c += path[i]->get_double_cost();
	}
	return c;
}

double IforkRootPath::get_needed_cost() const {
	return cost;
}

void IforkRootPath::set_needed_cost(double c) {
	cost = c;
}

void IforkRootPath::get_path_support(int v, vector<int>& support) const {

	for (int i=0; i< path.size(); i++) {
		int prv = path[i]->get_prevail_val(v);
		if (-1 != prv) {
			support.push_back(prv);
		}
	}
}

bool IforkRootPath::is_dominated(IforkRootPath* path_b) const {
// Checks if the path is dominated by path_b, i.e. costs no more in every evaluated state
	if (cost > path_b->get_needed_cost())
		return false;

	for (int i=0; i< num_vars; i++) {
		if ((-1 != first_needed[i]) && (first_needed[i] != path_b->get_first_needed(i)))
			return false;
	}
	return true;
}

void IforkRootPath::get_applicable_vals(int root_bound, vector<int>& vals) const {

	// If the first value is defined, then the path is applicable only in this value.
	// otherwise it is applicable in every value that is not on the path.
	int val = path[0]->get_pre_val(0);
	if (-1 != val) {
		vals.push_back(val);
		return;
	}

	vector<int> inapplicable;
	inapplicable.assign(root_bound,-1);
	for (int i=0; i< path.size(); i++) {
		int post = path[i]->get_post_val(0);
		inapplicable[post] = 0;
	}
	// returning everything that wasn't marked
	for (int i=0; i< root_bound; i++) {
		if (inapplicable[i] != 0)
			vals.push_back(i);
	}
}

LPConstraint* IforkRootPath::get_LP_constraint() {
	return lpc;
}

void IforkRootPath::set_LP_constraint(LPConstraint* c) {
	lpc = c;
}

void IforkRootPath::dump() const {
	cout << "Path of length " << path.size() << endl;
	for (int i=0; i< path.size(); i++) {
		path[i]->dump();
	}
	cout << "Needed support from " << num_vars-1 << " parents: ";
	for (int i=1; i<num_vars; i++) {
		cout << " " << first_needed[i];
	}
	cout << endl << "Total cost: "<< cost << endl;
}
