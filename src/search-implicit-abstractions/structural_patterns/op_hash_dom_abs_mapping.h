#ifndef OP_HASH_DOM_ABS_MAPPING_H_
#define OP_HASH_DOM_ABS_MAPPING_H_

#include "dom_abs_mapping.h"
#include "op_hash_mapping.h"

class OpHashDomAbsMapping: public virtual DomainAbstractionMapping,
		public virtual OpHashMapping {
public:
	OpHashDomAbsMapping();
	virtual ~OpHashDomAbsMapping();

	virtual const State* get_abs_state(const State* state) const;

	virtual int get_abs_operators(Operator* o, vector<Operator*>& abs_ops);

	virtual Operator* get_orig_operator(Operator* o) const;

};

#endif /* OP_HASH_DOM_ABS_MAPPING_H_ */
