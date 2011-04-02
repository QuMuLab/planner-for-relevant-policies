#ifndef MAPPING_H_
#define MAPPING_H_

#include <vector>
#include "../state.h"
#include "../problem.h"
#include "../operator.h"

class Mapping {

protected:

	const Problem* original;
	Problem* abstract;

	const State* curr_state;
	state_var_t* curr_buf;
public:
	const Problem* get_original() const {return original;}
	Problem* get_abstract() const {return abstract;}

	virtual const State* get_abs_state(const State* state) const = 0;

	virtual int get_abs_operators(Operator* o, vector<Operator*>& abs_ops) = 0;
	virtual Operator* get_orig_operator(Operator* o) const = 0;

	Mapping(const Problem* orig, Problem* abs);
	Mapping();
	virtual ~Mapping();

	void set_original(const Problem* p);
	void set_abstract(Problem* p);

	bool is_goal_in_abstraction(const State* state);
	void remove_abstract_operators() {abstract->delete_operators();}

};

#endif /* MAPPING_H_ */
