#include "op_hash_dom_abs_mapping.h"

OpHashDomAbsMapping::OpHashDomAbsMapping() {

}

OpHashDomAbsMapping::~OpHashDomAbsMapping() {
}

const State* OpHashDomAbsMapping::get_abs_state(const State* state) const {
	return DomainAbstractionMapping::get_abs_state(state);
}

int OpHashDomAbsMapping::get_abs_operators(Operator* o, vector<Operator*>& abs_ops) {
	return OpHashMapping::get_abs_operators(o, abs_ops);
}

Operator* OpHashDomAbsMapping::get_orig_operator(Operator* o) const {
	return OpHashMapping::get_orig_operator(o);
}
