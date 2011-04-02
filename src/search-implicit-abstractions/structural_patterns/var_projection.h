#ifndef VARPROJECTION_H_
#define VARPROJECTION_H_

#include "general_abstraction.h"
#include <vector>
#include "var_proj_mapping.h"
#include "../problem.h"


class VariablesProjection: public virtual GeneralAbstraction {
	vector<int> ptrn;
public:
	VariablesProjection(vector<int>& pattern);
	VariablesProjection();
	virtual ~VariablesProjection();
	virtual void create(const Problem* p);
	virtual void set_pattern(vector<int>& pattern);
	virtual void set_root_var_and_domain(Domain*) {};

	void abstract_prevail(vector<Prevail> prevail, vector<Prevail>& prv, const vector<int>& abs_vars);
	void abstract_prepost(vector<PrePost> prepost, vector<PrePost>& pre, const vector<int>& abs_vars);

//	void abstract_action(Operator* op, 	vector<Operator*>& abs_op, vector <int>& abs_vars);
	virtual void abstract_action(const vector<int>& abs_vars, Operator* op, vector<Operator*>& abs_op);

};

#endif /* VARPROJECTION_H_ */
