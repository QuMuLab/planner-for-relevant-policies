#ifndef GENERAL_ABSTRACTION_H_
#define GENERAL_ABSTRACTION_H_

#include "../problem.h"
#include "mapping.h"

class Domain {
	int var;
	int old_size, new_size;
	vector<int> new_domain;
	vector<vector<int> > old_domain;
public:
	Domain();
	Domain(int v, int old_sz, int new_sz);
	virtual ~Domain();

	void set_var(int v, int old_sz, int new_sz);
	void update_var(int v);
	void set_value(int orig_val, int abs_val);
	int get_var();
	int get_old_size();
	int get_new_size();

	void get_orig_values(int abs_val, vector<int>& ret) const;
	int get_abs_value(int orig_val) const;

	void dump() const;

};


class GeneralAbstraction {

private:
	Mapping* m;
	int abstraction_type;

public:
	GeneralAbstraction();
	virtual ~GeneralAbstraction();

	virtual void create(const Problem* p) = 0;
//	virtual void set_abstract_costs(vector<double>& costs) = 0;
	virtual void set_root_var_and_domain(Domain* new_dom) = 0;
	virtual void set_pattern(vector<int>& pattern) = 0;
	virtual void abstract_action(const vector<int>& abs_vars, Operator* op, vector<Operator*>& abs_op) = 0;
	virtual void abstract_actions(const vector<int>& abs_vars, const vector<Operator*>& orig_ops,
			vector<Operator*>& ops, vector<pair<Operator*, Operator*> >& ops_to_add);

	Mapping* get_mapping() const;
	void set_mapping(Mapping* map);

	int get_abstraction_type() const;
	void set_abstraction_type(int type);
	void remove_abstract_operators() {m->remove_abstract_operators();}
};

#endif /* GENERAL_ABSTRACTION_H_ */
