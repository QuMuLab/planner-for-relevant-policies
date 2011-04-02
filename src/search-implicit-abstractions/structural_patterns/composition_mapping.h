#ifndef COMPOSITION_MAPPING_H_
#define COMPOSITION_MAPPING_H_

#include "mapping.h"
#include <set>

class CompositionMapping: public Mapping {
	Mapping* from_map;
	Mapping* to_map;

public:
	CompositionMapping(Mapping* a, Mapping* b);
	virtual ~CompositionMapping();

	virtual const State* get_abs_state(const State* state) const;

	virtual int get_abs_operators(Operator* o, vector<Operator*>& abs_ops);
	virtual Operator* get_orig_operator(Operator* o) const;

};

#endif /* COMPOSITION_MAPPING_H_ */
