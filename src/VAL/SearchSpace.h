#ifndef __SEARCHSPACE
#define __SEARCHSPACE

#include "Validator.h"
#include "ptree.h"
#include "graphconstruct.h"
#include "TIM.h"
#include "PartialPlan.h"

#include <queue>

namespace Planner {

// This is a singleton object....

class SearchSpace {
private:
// We need all these things to build a Validator object that can then be used to 
// support the simulation process for execution of Happenings.
	VAL::DerivationRules derivRules;
	VAL::plan dummyPlan;
	VAL::Validator val;

	Inst::GraphFactory * gf;
	Inst::PlanGraph pg;

	typedef std::priority_queue<PartialPlan *,vector<PartialPlan *>,PartialPlanOrderer> PPQueue;
	PPQueue * ppq;

	bool hasOrder;
	PartialPlanOrder * myPPO;
	
	SearchSpace();
	SearchSpace(const SearchSpace &);
	
public:
	static SearchSpace & instance() 
	{
		static SearchSpace ssp;
		return ssp;
	};

	~SearchSpace()
	{
		delete myPPO;
	};
	
	void setOrdering(PartialPlanOrder * ppo)
	{
		if(hasOrder)
		{
			PPQueue * ppq1 = new PPQueue(PartialPlanOrderer(ppo));
			
			while(!ppq->empty())
			{
				ppq1->push(ppq->top());
				ppq->pop();
			};
			delete ppq;
			ppq = ppq1;
			delete myPPO;
			myPPO = ppo;
		}
		else
		{
			ppq = new PPQueue(PartialPlanOrderer(ppo));
			myPPO = ppo;
			hasOrder = true;
		};
	};
	
	VAL::Validator * getVal() {return &val;};
	VAL::plan * getDummyPlan() {return &dummyPlan;};
	Inst::PlanGraph & getPG() {return pg;};


	void findPlan();
};



};



#endif
