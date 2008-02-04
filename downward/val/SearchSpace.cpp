#include "SearchSpace.h"

namespace Planner {

SearchSpace::SearchSpace() :
	derivRules(VAL::current_analysis->the_domain->drvs,VAL::current_analysis->the_domain->ops),
	val(&derivRules,0.001,*VAL::theTC,VAL::current_analysis->the_domain->ops,VAL::current_analysis->the_problem->initial_state,
				&dummyPlan,VAL::current_analysis->the_problem->metric,true,true,0,0),
	gf(new Inst::GraphFactory()), 
	pg(gf), ppq(0), hasOrder(false), myPPO(0)
{
	pg.extendToGoals();
};


void SearchSpace::findPlan()
{
	if(!hasOrder)
	{
		cout << "You have to set the ordering for Partial Plans before searching for a plan\n";
		exit(0);
	};
	PartialPlan * pp = new PartialPlan();
	cout << "Our first partial plan:\n" << *pp << "\n";
	ppq->push(pp);

	cout << "Let's embark on our search for a plan....\n";
	cout << "Our story begins with\n" << *(ppq->top()) << "\n";

	cout << "First we wait epsilon\n";
	pp->initialWait(val.getTolerance());
	ppq->pop();
	ppq->push(pp);
	cout << "Now we have:\n" << *pp << "\n";
	pp->timeToTrigger();
};
	
};
