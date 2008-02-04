#include <cstdio>
#include <iostream>
#include <fstream>
#include "ptree.h"
#include <FlexLexer.h>
#include "instantiation.h"
#include "SimpleEval.h"
#include "DebugWriteController.h"
#include "typecheck.h"
#include "TIM.h"

#include "graphconstruct.h"
#include "SearchSpace.h"
#include "PartialPlan.h"

using std::ifstream;
using std::cerr;

using namespace TIM;
using namespace Inst;
using namespace VAL;
using namespace Planner;

namespace VAL {
bool ContinueAnyway;
bool ErrorReport;
bool InvariantWarnings;
bool LaTeX;
bool makespanDefault;
};

int main(int argc,char * argv[])
{
	performTIMAnalysis(&argv[1]);

	SimpleEvaluator::setInitialState();
    for(operator_list::const_iterator os = current_analysis->the_domain->ops->begin();
    			os != current_analysis->the_domain->ops->end();++os)
    {
    	cout << (*os)->name->getName() << "\n";
    	instantiatedOp::instantiate(*os,current_analysis->the_problem,*theTC);
    	cout << instantiatedOp::howMany() << " so far\n";
    };
    cout << instantiatedOp::howMany() << "\n";
    //instantiatedOp::writeAll(cout);

	//cout << "\nList of all literals:\n";
    instantiatedOp::createAllLiterals(current_analysis->the_problem,theTC);
    //instantiatedOp::writeAllLiterals(cout);

    Inst::ActEntry::readDurations(argv[3]);

	SearchSpace::instance().setOrdering(new LongPlanHead);
	SearchSpace::instance().findPlan();
	
}
