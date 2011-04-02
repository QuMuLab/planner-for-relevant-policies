#include "var_proj_mapping.h"

VarProjMapping::VarProjMapping(const Problem* orig, Problem* abs, vector<int> orig_vars,  vector<int> abs_vars) {

	set_original(orig);
	set_abstract(abs);

	set_original_vars(orig_vars);
	set_abstract_vars(abs_vars);


}

VarProjMapping::VarProjMapping() {

}

VarProjMapping::~VarProjMapping() {
	// TODO Auto-generated destructor stub
}

vector<int> VarProjMapping::get_original_vars() const {
	return original_vars;
}

void VarProjMapping::set_original_vars(vector<int> vars){
	original_vars = vars;
}

vector<int> VarProjMapping::get_abstract_vars() const {
	return abstract_vars;
}

void VarProjMapping::set_abstract_vars(vector<int> vars){
	abstract_vars = vars;
}

int VarProjMapping::get_original_var(int abs) const {
	return original_vars[abs];
}

int VarProjMapping::get_abstract_var(int orig) const{
	return abstract_vars[orig];
}


const State* VarProjMapping::get_abs_state(const State* state) const {

	int var_count = original_vars.size();


	for(int i = 0; i < var_count; i++)
		curr_buf[i] = state->get_buffer()[original_vars[i]];

	return curr_state;
}
