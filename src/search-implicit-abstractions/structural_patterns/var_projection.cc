#include "var_projection.h"
#include "../problem.h"
#include <vector>
#include "var_proj_mapping.h"
#include "../operator.h"
#include "domain_abstraction.h"
#include "op_hash_var_proj_mapping.h"
#include "op_hash_mapping.h"
#include <string>


VariablesProjection::VariablesProjection() {

}

VariablesProjection::VariablesProjection(vector<int>& pattern) {
	set_pattern(pattern);
}

VariablesProjection::~VariablesProjection() {
}

void VariablesProjection::set_pattern(vector<int>& pattern){
	ptrn = pattern;
}

void VariablesProjection::abstract_prevail(vector<Prevail> prevail, vector<Prevail>& prv, const vector<int>& abs_vars) {
	for(int it = 0; it < prevail.size(); it++) {
		int abs_var = abs_vars[prevail[it].var];
		if (-1 != abs_var) {
			prv.push_back(Prevail(abs_var,prevail[it].prev));
		}
	}
}


void VariablesProjection::abstract_prepost(vector<PrePost> prepost, vector<PrePost>& pre, const vector<int>& abs_vars) {
	for(int it = 0; it < prepost.size(); it++) {
		int abs_var = abs_vars[prepost[it].var];
		if (-1 != abs_var) {
			vector<Prevail> new_cond;
			abstract_prevail(prepost[it].cond, new_cond, abs_vars);
			pre.push_back(PrePost(abs_var,prepost[it].pre,prepost[it].post,new_cond));
		}
	}
}



void VariablesProjection::create(const Problem* p) {

	//TODO: This function should be rewritten!!!
	//Creating the empty mapping
	OpHashVarProjMapping* map = new OpHashVarProjMapping();
	map->set_original(p);

	const vector<string> &orig_name = p->get_variable_names();
	const vector<int> &orig_dom = p->get_variable_domains();

	// Creating abstract variables, initial state.
	vector<int> abs_vars;
	int var_count = ptrn.size();
//	orig_vars.resize(var_count);
	abs_vars.assign(orig_dom.size(),-1);

	vector<string> var_name;
	vector<int> var_domain;

	var_name.resize(var_count);
	var_domain.resize(var_count);

	for(int i = 0; i < var_count; i++){
		var_name[i] = orig_name[ptrn[i]];
		var_domain[i] = orig_dom[ptrn[i]];
		abs_vars[ptrn[i]] = i;
	}

	map->set_original_vars(ptrn);
	map->set_abstract_vars(abs_vars);

	state_var_t* buf = new state_var_t[var_count];
    for(int i = 0; i < var_count; i++)
          buf[i] = p->get_initial_state()->get_buffer()[ptrn[i]];

//	const State* init_state = new State(buf, var_count);
	const State* init_state = new State(buf);

	// Creating abstract goal
	vector<pair<int, int> > orig_goal;
	p->get_goal(orig_goal);
	vector<pair<int, int> > g;
	for(int i = 0; i < orig_goal.size() ; i++){
		if (-1 != abs_vars[orig_goal[i].first]){
			pair<int, int> new_goal;
			new_goal.first = abs_vars[orig_goal[i].first];
			new_goal.second = orig_goal[i].second;
			g.push_back(new_goal);
		}
	}

	// Creating abstract actions
	const vector<Operator*> &orig_ops = p->get_operators();

	vector<Operator*> ops, axioms;
	vector<pair<Operator*, Operator*> > ops_to_add;
	vector<Operator> axi = p->get_axioms();
	for(int i = 0; i < axi.size(); i++){
		axioms.push_back(&axi[i]);
	}

	abstract_actions(abs_vars,orig_ops,ops,ops_to_add);
	abstract_actions(abs_vars,axioms,ops,ops_to_add);

	vector<Operator> no_axioms;
	Problem* abs_prob = new Problem(var_name, var_domain, init_state, g, ops, no_axioms);

	map->set_abstract(abs_prob);
	map->initialize();

	for (int i = 0; i < ops_to_add.size(); i++)
		map->add_abs_operator(ops_to_add[i].first,ops_to_add[i].second);

	set_mapping(map);

}

void VariablesProjection::abstract_action(const vector <int>& abs_vars, Operator* op,	vector<Operator*>& abs_op){

	vector<Prevail> prv;
	abstract_prevail(op->get_prevail(),prv,abs_vars);
	vector<PrePost> pre;
	abstract_prepost(op->get_pre_post(),pre,abs_vars);
	if (0 == pre.size()) return;
	string nm;
#ifdef DEBUGMODE

	nm = op->get_name();
	const int max_str_len(42);
	char my_string[max_str_len+1];
	snprintf(my_string, max_str_len, "::%#x", (unsigned int) this);
	nm += my_string;

#endif
	Operator* new_op = new Operator(op->is_axiom(),prv, pre, nm, op->get_double_cost());
	abs_op.push_back(new_op);
}
