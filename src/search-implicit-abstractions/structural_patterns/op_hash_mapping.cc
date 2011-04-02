#include "op_hash_mapping.h"

OpHashMapping::OpHashMapping(const Problem* orig, Problem* abs) {

	set_original(orig);
	set_abstract(abs);

//	original = orig;
//	abstract = abs;
//	original_ops.resize(abstract->get_actions_number());

}

OpHashMapping::OpHashMapping() {

}

OpHashMapping::~OpHashMapping() {
	// TODO Auto-generated destructor stub

/*
	for (hash_map<int, vector<Operator*>* >::iterator ii = beta_func.begin(); ii != beta_func.end(); ++ii){
		delete ii->second;
	}
	beta_func.clear();
*/
}

void OpHashMapping::initialize() {
	original_ops.resize(abstract->get_actions_number());

}
int OpHashMapping::get_abs_operators(Operator* o, vector<Operator*>& abs_ops) {

	int o_index = original->get_action_index(o);

	if (beta_func.find(o_index) == beta_func.end()) {
		return 0;
	}
	vector<Operator*> ops = *(beta_func[o_index]);
	for (int i=0;i<ops.size();i++) {
		abs_ops.push_back(ops[i]);
	}
	return ops.size();
}


Operator* OpHashMapping::get_orig_operator(Operator* o) const {

	int orig_index = original_ops[abstract->get_action_index(o)];

	return original->get_action_by_index(orig_index);
}


void OpHashMapping::add_abs_operator(Operator* o, Operator* a) {

	int o_index = original->get_action_index(o);
	int a_index = abstract->get_action_index(a);

	if (beta_func.find(o_index) == beta_func.end()) {
		beta_func[o_index] = new vector<Operator*>;
	}

	beta_func[o_index]->push_back(a);
	original_ops[a_index] = o_index;

}
