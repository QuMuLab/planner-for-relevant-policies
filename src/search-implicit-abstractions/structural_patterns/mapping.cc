#include "mapping.h"

#include "../state.h"
#include "../problem.h"
#include "../operator.h"
#include <vector>

//Mapping::Mapping(const Problem* orig, const Problem* abs) {
Mapping::Mapping(const Problem* orig, Problem* abs) {
	abstract = NULL;
	curr_state = NULL;

	set_original(orig);
	set_abstract(abs);
}

Mapping::Mapping() {
	abstract = NULL;
	curr_state = NULL;
}

Mapping::~Mapping() {
	if (abstract)
		delete abstract;
	if (curr_state)
		delete curr_state;
}

void Mapping::set_original(const Problem* p) {original = p;}

void Mapping::set_abstract(Problem* p) {
	if (abstract)
		delete abstract;
	if (curr_state)
		delete curr_state;

	abstract = p;

	int num = abstract->get_vars_number();
	curr_buf = new state_var_t[num];
//	curr_state = new State(curr_buf, num);
	curr_state = new State(curr_buf);
}

bool Mapping::is_goal_in_abstraction(const State* state) {
	return abstract->is_goal(get_abs_state(state));
}
