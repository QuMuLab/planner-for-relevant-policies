#include "domain_abstraction.h"
#include "op_hash_dom_abs_mapping.h"
#include "op_hash_mapping.h"
#include "var_proj_mapping.h"
#include <string>


Domain::Domain() {

}

Domain::Domain(int v, int old_sz, int new_sz) {
	set_var(v, old_sz, new_sz);
}

Domain::~Domain() {

}

void Domain::set_var(int v, int old_sz, int new_sz) {
	var = v;
	old_size = old_sz;
	new_size = new_sz;
	new_domain.assign(old_size, -1);
//	old_domain.reserve(new_size);
}

void Domain::update_var(int v) {
	var = v;
}

int Domain::get_var() {
	return var;
}
int Domain::get_old_size() {
	return old_size;
}
int Domain::get_new_size() {
	return new_size;
}


void Domain::set_value(int orig_val, int abs_val) {
	new_domain[orig_val] = abs_val;
}


void Domain::get_orig_values(int abs_val, vector<int>& ret) const {

	for (int i = 0; i < old_size; i++)
		if (new_domain[i] == abs_val)
			ret.push_back(i);
}


int Domain::get_abs_value(int orig_val) const {

	if ((orig_val >= 0) && (orig_val < old_size)) {
		int ret = new_domain[orig_val];
		return ret;
	}
	return -1;
}


void Domain::dump() const {
	cout<< "Domain for variable " << var << endl;
	for (int i = 0; i < old_size; i++)
		cout << "  "<< i << " => " << new_domain[i] << endl;
}



DomainAbstraction::DomainAbstraction() {

}

DomainAbstraction::DomainAbstraction(Domain* new_dom){
//	set_domain(new_dom);
	set_root_var_and_domain(new_dom);
}


DomainAbstraction::~DomainAbstraction() {
}

//void DomainAbstraction::set_domain(Domain* new_dom){
void DomainAbstraction::set_root_var_and_domain(Domain* new_dom){
	dom = new_dom;
}

void DomainAbstraction::get_orig_values(int abs_val, vector<int>& ret) const {

	dom->get_orig_values(abs_val,ret);
//	return dom->get_orig_values(abs_val);
}


int DomainAbstraction::get_abs_value(int orig_val) const {
	return dom->get_abs_value(orig_val);
}

void DomainAbstraction::abstract_prevail(const vector<Prevail>& prevail, vector<Prevail>& prv) {
//	vector<Prevail> prv;
	for(int i =0 ;i < prevail.size(); i++) {
		if (prevail[i].var == dom->get_var())
			prv.push_back(Prevail(prevail[i].var,get_abs_value(prevail[i].prev)));
		else
			prv.push_back(Prevail(prevail[i].var,prevail[i].prev));
	}
//	return prv;
}


void DomainAbstraction::abstract_prepost(const vector<PrePost>& prepost, vector<PrePost>& pre) {
	for(int it = 0; it < prepost.size(); it++) {
		// Get abstracted condition
		vector<Prevail> new_cond;
		abstract_prevail(prepost[it].cond, new_cond);
		int new_pre = prepost[it].pre;
		int new_post = prepost[it].post;

		if (prepost[it].var == dom->get_var()){
			new_pre = get_abs_value(prepost[it].pre);
			new_post = get_abs_value(prepost[it].post);
			assert(new_post >= 0);
			if (new_pre == new_post)
				continue;
		}
		pre.push_back(PrePost(prepost[it].var,new_pre,new_post,new_cond));
	}
}





void DomainAbstraction::create(const Problem* p) {
	//Creating the empty mapping
	OpHashDomAbsMapping* map = new OpHashDomAbsMapping();
	map->set_original(p);
	map->set_domain(dom);

	// Creating abstract variables, initial state.
	const vector<string> &var_name = p->get_variable_names();
	const vector<int> &var_domain = p->get_variable_domains();

	int var_count = var_name.size();
	const State* state = p->get_initial_state();

	vector<int> new_var_domain;
	new_var_domain.resize(var_count);
	state_var_t* buf = new state_var_t[var_count];
	for(int i = 0; i < var_count; i++){
		if (i == dom->get_var()){
			new_var_domain[i] = dom->get_new_size();
			buf[i] = (state_var_t) dom->get_abs_value((int) state->get_buffer()[i]);
		} else {
			new_var_domain[i] = var_domain[i];
			buf[i] = state->get_buffer()[i];
		}
	}

//	const State* init_state = new State(buf, var_count);
	const State* init_state = new State(buf);

	// Creating abstract goal
	vector<pair<int, int> > new_goal;
	p->get_goal(new_goal);
	for(int i = 0; i < new_goal.size() ; i++){
		if (dom->get_var() == new_goal[i].first)
			new_goal[i].second = get_abs_value(new_goal[i].second);
	}

	// Creating abstract action
	const vector<Operator*> &orig_ops = p->get_operators();

	vector<Operator*> ops, axioms;
//	int num_orig_ops = orig_ops.size();

	vector<pair<Operator*, Operator*> > ops_to_add;
	vector<Operator> axi = p->get_axioms();
	for(int i = 0; i < axi.size(); i++){
		axioms.push_back(&axi[i]);
	}
	const vector<int> abs_vars;

	abstract_actions(abs_vars,orig_ops,ops,ops_to_add);
	abstract_actions(abs_vars,axioms,ops,ops_to_add);

	vector<Operator> no_axioms;
	Problem* abs_prob = new Problem(var_name, new_var_domain, init_state, new_goal, ops, no_axioms, false);

	map->set_abstract(abs_prob);
	map->initialize();
//	abs_prob->dump();

//	cout << "Actions added to the problem - domain abstraction" << endl;
	for (int i = 0; i < ops_to_add.size(); i++) {
		map->add_abs_operator(ops_to_add[i].first,ops_to_add[i].second);
//		ops_to_add[i].first->dump();
//		ops_to_add[i].second->dump();
	}
	set_mapping(map);

}

// Creates abstract actions vector (freeing this vector is up to user)
void DomainAbstraction::abstract_action(const vector<int>& , Operator* op, vector<Operator*>& abs_op){

	vector<Prevail> prv;
	abstract_prevail(op->get_prevail(),prv);
	vector<PrePost> pre;
	abstract_prepost(op->get_pre_post(),pre);
	if (0 == pre.size()) {
		return;
	}
	string nm;
#ifdef DEBUGMODE
	nm = op->get_name()+string("::");
	const int max_str_len(42);
	char my_string[max_str_len+1];
	snprintf(my_string, max_str_len, "%#x", (unsigned int) this);
	nm += my_string;
#endif

	Operator* new_op = new Operator(op->is_axiom(), prv, pre, nm, op->get_double_cost());
	abs_op.push_back(new_op);
}
