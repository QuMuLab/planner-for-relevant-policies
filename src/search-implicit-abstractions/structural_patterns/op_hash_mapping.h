#ifndef OP_HASH_MAPPING_H_
#define OP_HASH_MAPPING_H_

using namespace std;
#include <ext/hash_map>

using namespace __gnu_cxx;

#include <vector>


#include "mapping.h"

class OpHashMapping: public virtual Mapping {

protected:

	vector<int> original_ops;

	hash_map<int, vector<Operator*>* > beta_func;

public:
	OpHashMapping(const Problem* orig, Problem* abs);
	OpHashMapping();
	virtual ~OpHashMapping();

	void initialize();

	virtual const State* get_abs_state(const State* state) const = 0;

	virtual int get_abs_operators(Operator* o, vector<Operator*>& abs_ops);

	virtual Operator* get_orig_operator(Operator* o) const;

	void add_abs_operator(Operator *o, Operator* a);

};

#endif /* OP_HASH_MAPPING_H_ */
