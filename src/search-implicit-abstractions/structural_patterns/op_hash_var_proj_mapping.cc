#include "op_hash_var_proj_mapping.h"

OpHashVarProjMapping::OpHashVarProjMapping() {

}

OpHashVarProjMapping::~OpHashVarProjMapping() {
}

const State* OpHashVarProjMapping::get_abs_state(const State* state) const {
	return VarProjMapping::get_abs_state(state);
}

int OpHashVarProjMapping::get_abs_operators(Operator* o, vector<Operator*>& abs_ops) {
	return OpHashMapping::get_abs_operators(o,abs_ops);
}

Operator* OpHashVarProjMapping::get_orig_operator(Operator* o) const {
	return OpHashMapping::get_orig_operator(o);
}
