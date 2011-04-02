#ifndef FORKS_ABSTRACTION_H_
#define FORKS_ABSTRACTION_H_

#include "general_abstraction.h"

class ForksAbstraction: public virtual GeneralAbstraction {
protected:
	int var;
	vector<int> leafs; // TODO: check if it is used;

	bool is_singleton;
	bool is_empty;
	bool is_var_singleton;

public:
	ForksAbstraction();
	ForksAbstraction(int v);
	virtual ~ForksAbstraction();

	virtual void create(const Problem* p);
	virtual void set_root_var_and_domain(Domain* new_dom) { var = new_dom->get_var();}
	virtual void set_pattern(vector<int>&) {};

	void set_variable(int v);

	int get_root() const;
	void get_leafs(vector<int>& vars) const;
	bool is_empty_abstraction();

	bool is_singleton_abstraction();


//	virtual void abstract_action(const Problem* p, const vector<int>& abs_vars, Operator* op, vector<Operator*>& abs_op);
	virtual void abstract_action(const vector<int>& abs_vars, Operator* op, vector<Operator*>& abs_op);
	int root_prevail_index(Operator* op);
	int root_prepost_index(Operator* op);
	int root_unconditional_prepost_index(Operator* op);
	int get_value_for_var(int v, vector<Prevail>& prv);

	bool is_originally_singleton() {return is_var_singleton;}
};

#endif /* FORKS_ABSTRACTION_H_ */
