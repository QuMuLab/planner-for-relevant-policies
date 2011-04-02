#include "composition_mapping.h"
#include <vector>


CompositionMapping::CompositionMapping(Mapping* a, Mapping* b):from_map(a), to_map(b) {
	set_original(from_map->get_original());
	set_abstract(to_map->get_abstract());
}

CompositionMapping::~CompositionMapping() {
}



const State* CompositionMapping::get_abs_state(const State* state) const {
/*	const State* s = from_map->get_abs_state(state);
	const State* ret = to_map->get_abs_state(s);
	delete s;
	return ret;*/

	return to_map->get_abs_state(from_map->get_abs_state(state));
}

int CompositionMapping::get_abs_operators(Operator* o, vector<Operator*>& abs_ops){

	vector<Operator*> ops;
	from_map->get_abs_operators(o,ops);

	int tot = 0;
	for(int i = 0; i < ops.size(); i++){
		tot += to_map->get_abs_operators(ops[i],abs_ops);
	}
	return tot;
}


Operator* CompositionMapping::get_orig_operator(Operator* o) const {

	return from_map->get_orig_operator(to_map->get_orig_operator(o));
}


