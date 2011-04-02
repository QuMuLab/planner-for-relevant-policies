#ifndef BINARY_FORKS_H_
#define BINARY_FORKS_H_

#include "forks_abstraction.h"
#include "domain_abstraction.h"

class BinaryForksAbstraction: public ForksAbstraction {
	Domain* dom;
public:
	BinaryForksAbstraction();
	BinaryForksAbstraction(Domain* new_dom);
	BinaryForksAbstraction(ForksAbstraction* f, Domain* new_dom);

	virtual ~BinaryForksAbstraction();

	virtual void create(const Problem* p);
	void set_root_var_and_domain(Domain* new_dom);


};

#endif /* BINARY_FORKS_H_ */
