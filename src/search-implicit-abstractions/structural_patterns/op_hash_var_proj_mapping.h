#ifndef OP_HASH_VAR_PROJ_MAPPING_H_
#define OP_HASH_VAR_PROJ_MAPPING_H_

#include "op_hash_mapping.h"
#include "var_proj_mapping.h"

class OpHashVarProjMapping: public virtual OpHashMapping, public virtual VarProjMapping {
public:
	OpHashVarProjMapping();
	virtual ~OpHashVarProjMapping();


	virtual const State* get_abs_state(const State* state) const;

	virtual int get_abs_operators(Operator* o, vector<Operator*>& abs_ops);

	virtual Operator* get_orig_operator(Operator* o) const;

};

#endif /* OP_HASH_VAR_PROJ_MAPPING_H_ */
