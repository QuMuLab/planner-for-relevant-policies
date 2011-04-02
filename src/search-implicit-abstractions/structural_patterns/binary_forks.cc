#include "binary_forks.h"
#include "domain_abstraction.h"
#include "composition_mapping.h"
#include "op_hash_var_proj_mapping.h"
#include "mapping.h"




BinaryForksAbstraction::BinaryForksAbstraction() {

}

BinaryForksAbstraction::BinaryForksAbstraction(Domain* new_dom){
	set_root_var_and_domain(new_dom);
}

BinaryForksAbstraction::BinaryForksAbstraction(ForksAbstraction* f, Domain* new_dom){
	set_root_var_and_domain(new_dom);
	set_mapping(f->get_mapping());
	set_abstraction_type(f->get_abstraction_type());
	if (f->is_empty_abstraction())
		return;
	if (2 == dom->get_old_size())
		return;
	// Binarization according to new_dom
	OpHashVarProjMapping* fork_map =  dynamic_cast<OpHashVarProjMapping*>(get_mapping());
	const Problem* abs_p = fork_map->get_abstract();

	int new_var = fork_map->get_abstract_var(dom->get_var());
	dom->update_var(new_var);

	DomainAbstraction bin(dom);
	bin.create(abs_p);
	Mapping* map = new CompositionMapping(fork_map,bin.get_mapping());
	set_mapping(map);
}

BinaryForksAbstraction::~BinaryForksAbstraction() {
//	Mapping* map = get_mapping();
//	delete map;
}

void BinaryForksAbstraction::set_root_var_and_domain(Domain* new_dom){
	dom = new_dom;

}

void BinaryForksAbstraction::create(const Problem* p) {
	ForksAbstraction::set_variable(dom->get_var());
	ForksAbstraction::create(p);
	if (is_empty)
		return;
	if (2 == dom->get_old_size())
		return;
	OpHashVarProjMapping* fork_map =  dynamic_cast<OpHashVarProjMapping*>(this->get_mapping());
	const Problem* abs_p = fork_map->get_abstract();

	int new_var = fork_map->get_abstract_var(dom->get_var());
	dom->update_var(new_var);

	DomainAbstraction bin(dom);
	bin.create(abs_p);
	Mapping* map = new CompositionMapping(fork_map,bin.get_mapping());
	this->set_mapping(map);
}


