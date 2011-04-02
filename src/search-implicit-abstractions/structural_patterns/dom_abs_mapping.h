#ifndef DOM_ABS_MAPPING_H_
#define DOM_ABS_MAPPING_H_

#include "mapping.h"
#include "domain_abstraction.h"

class DomainAbstractionMapping: public virtual Mapping {
protected:
	Domain* dom;

public:
	DomainAbstractionMapping();
	DomainAbstractionMapping(const Problem* orig, Problem* abs, Domain* d);
	virtual ~DomainAbstractionMapping();

	void set_domain(Domain* d);
	virtual const State* get_abs_state(const State* state) const;

	virtual int get_abs_operators(Operator* o, vector<Operator*>& abs_ops) = 0;
	virtual Operator* get_orig_operator(Operator* o) const = 0;

};

#endif /* DOM_ABS_MAPPING_H_ */
