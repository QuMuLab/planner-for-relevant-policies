#ifndef VAR_PROJ_MAPPING_H_
#define VAR_PROJ_MAPPING_H_

#include "mapping.h"

class VarProjMapping: public virtual Mapping {

protected:
	vector<int> abstract_vars;      // Holds abstract variables for each original variable
	vector<int> original_vars;		// Holds original variables for each abstract variable
public:
	VarProjMapping(const Problem* orig, Problem* abs, vector<int> orig_vars,  vector<int> abs_vars);
	VarProjMapping();
	virtual ~VarProjMapping();

	virtual const State* get_abs_state(const State* state) const;

	virtual int get_abs_operators(Operator* o, vector<Operator*>& abs_ops) = 0;
	virtual Operator* get_orig_operator(Operator* o) const = 0;

	vector<int> get_original_vars() const;
	void set_original_vars(vector<int> vars);

	vector<int> get_abstract_vars() const;
	void set_abstract_vars(vector<int> vars);

	int get_original_var(int abs) const;
	int get_abstract_var(int orig) const;

};

#endif /* VAR_PROJ_MAPPING_H_ */
