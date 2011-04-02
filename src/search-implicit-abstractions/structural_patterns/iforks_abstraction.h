#ifndef IFORKS_ABSTRACTION_H_
#define IFORKS_ABSTRACTION_H_

#include "general_abstraction.h"

class IforksAbstraction: public virtual GeneralAbstraction {
protected:
	int var;
	vector<int> parents; // TODO: check if it is used;

	bool is_singleton;
	bool is_empty;
	bool is_var_singleton;


public:
	IforksAbstraction();
	IforksAbstraction(int v);
	virtual ~IforksAbstraction();

	virtual void create(const Problem* p);
//	void set_variable(int v);
	virtual void set_root_var_and_domain(Domain* new_dom) { var = new_dom->get_var();}
	virtual void set_pattern(vector<int>&) {};

	int get_root() const;
	void get_parents(vector<int>& vars) const;
	bool is_empty_abstraction();

	bool is_singleton_abstraction();

	virtual void abstract_action(const vector<int>& abs_vars, Operator* op, vector<Operator*>& abs_op);

	int root_prepost_index(Operator* op);
	int root_unconditional_prepost_index(Operator* op);
	int get_value_for_var(int v, vector<Prevail>& prv);

	bool is_originally_singleton() {return is_var_singleton;}


};

#endif /* IFORKS_ABSTRACTION_H_ */
