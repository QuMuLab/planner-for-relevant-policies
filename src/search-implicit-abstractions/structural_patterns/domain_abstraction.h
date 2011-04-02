#ifndef DOMAIN_ABSTRACTION_H_
#define DOMAIN_ABSTRACTION_H_

#include "general_abstraction.h"


class DomainAbstraction: public GeneralAbstraction {
	Domain* dom;
public:
	DomainAbstraction();
	DomainAbstraction(Domain* new_dom);
	virtual ~DomainAbstraction();

	virtual void create(const Problem* p);
//	void set_domain(Domain* new_dom);
	virtual void set_root_var_and_domain(Domain* new_dom);
	virtual void set_pattern(vector<int>&) {};
	void get_orig_values(int abs_val, vector<int>& ret) const;
	int get_abs_value(int orig_val) const;

	void abstract_prevail(const vector<Prevail>& prevail, vector<Prevail>& prv);
	void abstract_prepost(const vector<PrePost>& prepost, vector<PrePost>& pre);
	virtual void abstract_action(const vector<int>& abs_vars, Operator* op, vector<Operator*>& abs_ops);

};

#endif /* DOMAIN_ABSTRACTION_H_ */
