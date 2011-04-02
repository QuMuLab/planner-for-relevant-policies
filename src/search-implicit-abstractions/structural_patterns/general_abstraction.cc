#include "general_abstraction.h"

GeneralAbstraction::GeneralAbstraction() { }

GeneralAbstraction::~GeneralAbstraction() {
//	if (m)
//		delete m;
}


Mapping* GeneralAbstraction::get_mapping() const {
	return m;
}

void GeneralAbstraction::set_mapping(Mapping* map) {
	m = map;
}

int GeneralAbstraction::get_abstraction_type() const {
	return abstraction_type;
}
void GeneralAbstraction::set_abstraction_type(int type) {
	abstraction_type = type;
}

void GeneralAbstraction::abstract_actions(const vector<int>& abs_vars, const vector<Operator*>& orig_ops,
		vector<Operator*>& ops, vector<pair<Operator*, Operator*> >& ops_to_add){
	for(int it = 0; it < orig_ops.size(); it++){
		vector<Operator*> abs_ops;
		abstract_action(abs_vars,orig_ops[it],abs_ops);
		for(int abs_it = 0; abs_it < abs_ops.size(); abs_it++){
			ops.push_back(abs_ops[abs_it]);
			pair<Operator*, Operator*> to_add;
			to_add.first = orig_ops[it];
			to_add.second = abs_ops[abs_it];
			ops_to_add.push_back(to_add);
		}
	}
}
