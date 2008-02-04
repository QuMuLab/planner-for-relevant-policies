#include "HowAnalyser.h"
#include "AbstractGraph.h"

namespace VAL {

HowAnalyser::HowAnalyser() : VisitController(), ag(new AbstractGraph())
{};

void HowAnalyser::visit_simple_effect(simple_effect * se)
{
	extended_pred_symbol * e = EPS(se->prop->head);
	if(epss.find(e) == epss.end())
	{
		ag->addInitialFact(e);
		epss.insert(e);
	};
};

void HowAnalyser::visit_action(action * a)
{
	cout << "Action: " << *(a->name) << "(" << *acts[a] << ")\n";
	acts[a]->analyse(a);
	ag->addAction(acts[a]);
};

void HowAnalyser::completeGraph()
{
	ag->develop();
};

};
