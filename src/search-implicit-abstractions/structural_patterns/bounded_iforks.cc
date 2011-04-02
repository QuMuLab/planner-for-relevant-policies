#include "bounded_iforks.h"
#include "domain_abstraction.h"
#include "projection_gen.h"
#include "composition_mapping.h"
#include "op_hash_var_proj_mapping.h"
#include "mapping.h"




BoundedIforksAbstraction::BoundedIforksAbstraction() {

}

BoundedIforksAbstraction::BoundedIforksAbstraction(Domain* new_dom){
	set_root_var_and_domain(new_dom);
}

BoundedIforksAbstraction::BoundedIforksAbstraction(IforksAbstraction* ifork, Domain* new_dom){
	set_root_var_and_domain(new_dom);
	set_mapping(ifork->get_mapping());
	set_abstraction_type(ifork->get_abstraction_type());
	if (ifork->is_empty_abstraction())
		return;
	if (dom->get_new_size() == dom->get_old_size())
		return;
	// Domain abstraction according to new_dom
	OpHashVarProjMapping* ifork_map =  dynamic_cast<OpHashVarProjMapping*>(get_mapping());
	const Problem* abs_p = ifork_map->get_abstract();
	int new_var = ifork_map->get_abstract_var(dom->get_var());
	dom->update_var(new_var);

	DomainAbstraction abstr(dom);
	abstr.create(abs_p);
	Mapping* map = new CompositionMapping(ifork_map,abstr.get_mapping());
	set_mapping(map);

	// Deal with variables that are not in the causal graph anymore
	const Problem* new_p = map->get_abstract();
	vector<int> new_pred = new_p->get_causal_graph()->get_predecessors(new_var);
	vector<int> old_pred = abs_p->get_causal_graph()->get_predecessors(new_var);
	if (new_pred.size() == old_pred.size())
		return;

//	cout << "Problem 1" << endl;
//	abs_p->dump();
//	cout << "Problem 2" << endl;
//	new_p->dump();
//	cout << "Additional abstraction from " << old_pred.size() + 1 << " variables to " << new_pred.size() +1 << endl;
	new_pred.insert(new_pred.begin(),new_var);
	VariablesProjection ptrn(new_pred);
	ptrn.create(new_p);
	Mapping* new_map = new CompositionMapping(map,ptrn.get_mapping());
	set_mapping(new_map);

}

BoundedIforksAbstraction::~BoundedIforksAbstraction() {
//	Mapping* map = get_mapping();
//	delete map;
}

void BoundedIforksAbstraction::set_root_var_and_domain(Domain* new_dom){
	dom = new_dom;

}

void BoundedIforksAbstraction::create(const Problem* p) {
	IforksAbstraction::set_root_var_and_domain(dom);
//	IforksAbstraction::set_variable(dom->get_var());
	IforksAbstraction::create(p);
	if (is_empty)
		return;
	if (dom->get_new_size() == dom->get_old_size())
		return;
	OpHashVarProjMapping* ifork_map =  dynamic_cast<OpHashVarProjMapping*>(this->get_mapping());
	const Problem* abs_p = ifork_map->get_abstract();

	int new_var = ifork_map->get_abstract_var(dom->get_var());
	dom->update_var(new_var);

	DomainAbstraction bin(dom);
	bin.create(abs_p);
	Mapping* map = new CompositionMapping(ifork_map,bin.get_mapping());
	this->set_mapping(map);
	// Deal with variables that are not in the causal graph anymore
	const Problem* new_p = map->get_abstract();
	vector<int> new_pred = new_p->get_causal_graph()->get_predecessors(new_var);
	vector<int> old_pred = abs_p->get_causal_graph()->get_predecessors(new_var);
	if (new_pred.size() == old_pred.size())
		return;

//	cout << "Problem 1" << endl;
//	abs_p->dump();
//	cout << "Problem 2" << endl;
//	new_p->dump();
//	cout << "Additional abstraction from " << old_pred.size() + 1 << " variables to " << new_pred.size() +1 << endl;
	new_pred.insert(new_pred.begin(),new_var);
	Projection ptrn(new_pred);
	ptrn.create(new_p);
	Mapping* new_map = new CompositionMapping(map,ptrn.get_mapping());
	this->set_mapping(new_map);
}

Domain* BoundedIforksAbstraction::get_domain() {
	return dom;
}


