#include "dom_abs_mapping.h"

DomainAbstractionMapping::DomainAbstractionMapping() {

}

DomainAbstractionMapping::DomainAbstractionMapping(const Problem* orig, Problem* abs, Domain* d) {
	set_original(orig);
	set_abstract(abs);

	set_domain(d);
}

DomainAbstractionMapping::~DomainAbstractionMapping() {
}

void DomainAbstractionMapping::set_domain(Domain* d) {
	dom = d;
}



const State* DomainAbstractionMapping::get_abs_state(const State* state) const {

	int var_count = abstract->get_vars_number();

	for(int i = 0; i < var_count; i++){
		if (i== dom->get_var()){
			curr_buf[i] = (state_var_t) dom->get_abs_value((int) state->get_buffer()[i]);
		} else {
			curr_buf[i] = state->get_buffer()[i];
		}
	}

	return curr_state;

}
