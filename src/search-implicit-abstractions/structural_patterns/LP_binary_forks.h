#ifndef LP_BINARY_FORKS_H_
#define LP_BINARY_FORKS_H_

#include "LP_binary_fork_gen.h"
#include "general_abstraction.h"

/* This class describes LP construction for forks with binary root domain as suggested
 * in the paper Optimal Additive Composition of Abstraction-based Admissible Heuristics.
 */

class LPBinaryForks: public LPBinaryFork {

public:
	LPBinaryForks();
	LPBinaryForks(GeneralAbstraction* abs);
	virtual ~LPBinaryForks();

	virtual void initiate();

};

#endif /* LP_BINARY_FORKS_H_ */
