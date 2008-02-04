#include <iostream>
#include "ptree.h"
#include "TIM.h"
#include "HowAnalyser.h"
#include "FuncAnalysis.h"
#include "AbstractGraph.h"

using namespace TIM;
using namespace VAL;
//using namespace Inst;



int main(int argc,char * argv[])
{
	FAverbose = false;
	performTIMAnalysis(&argv[1]);

	HowAnalyser ha;

	current_analysis->the_domain->predicates->visit(&ha);
	current_analysis->the_domain->ops->visit(&ha);
	current_analysis->the_problem->initial_state->visit(&ha);
	ha.completeGraph();
};
