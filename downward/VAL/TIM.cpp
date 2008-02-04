#include "FastEnvironment.h"
#include "TimSupport.h"
#include <cstdio>
#include <iostream>
#include <fstream>
#include "ptree.h"
#include <FlexLexer.h>
#include "TypedAnalyser.h"
#include "TIM.h"


extern int yyparse();
extern int yydebug;

using std::ifstream;
using std::ofstream;
using std::ostream;

namespace VAL {

bool Verbose = false;
ostream * report = &cout;
parse_category* top_thing=NULL;

analysis* current_analysis;

yyFlexLexer* yfl;
TypeChecker * theTC;
extern bool FAverbose;

int PropInfo::x = 0;

};

char * current_filename;
using namespace VAL;

namespace TIM {


TIMAnalyser * TA;



void performTIMAnalysis(char * argv[])
{
    current_analysis = new analysis;
    IDopTabFactory * fac = new IDopTabFactory;
    current_analysis->setFactory(fac);
    current_analysis->pred_tab.replaceFactory<holding_pred_symbol>();
    current_analysis->func_tab.replaceFactory<extended_func_symbol>();
    current_analysis->const_tab.replaceFactory<TIMobjectSymbol>();
    current_analysis->op_tab.replaceFactory<TIMactionSymbol>();
    current_analysis->setFactory(new TIMfactory());
    auto_ptr<EPSBuilder> eps(new specEPSBuilder<TIMpredSymbol>());
    Associater::buildEPS = eps;
    
    ifstream* current_in_stream;
    yydebug=0; // Set to 1 to output yacc trace 

    yfl= new yyFlexLexer;

    // Loop over given args

	for(int i = 0;i < 2;++i)
	{
		current_filename= argv[i];
	//	cout << "File: " << current_filename << '\n';
		current_in_stream = new ifstream(current_filename);
		if (current_in_stream->bad())
		{
		    // Output a message now
		    cout << "Failed to open\n";
		    
		    // Log an error to be reported in summary later
		    line_no= 0;
		    log_error(E_FATAL,"Failed to open file");
		}
		else
		{
		    line_no= 1;

		    // Switch the tokeniser to the current input stream
		    yfl->switch_streams(current_in_stream,&cout);
		    yyparse();

		    // Output syntax tree
		    //if (top_thing) top_thing->display(0);
		}
		delete current_in_stream;
    }
    // Output the errors from all input files
//    current_analysis->error_list.report();
    delete yfl;

    DurativeActionPredicateBuilder dapb;
    current_analysis->the_domain->visit(&dapb);

	theTC = new TypeChecker(current_analysis);
    
    TypePredSubstituter a;
    current_analysis->the_problem->visit(&a);
   	current_analysis->the_domain->visit(&a); 

   	Analyser aa(dapb.getIgnores());
   	current_analysis->the_problem->visit(&aa);
   	current_analysis->the_domain->visit(&aa);

//    current_analysis->the_domain->predicates->visit(&aa);

	if(FAverbose && current_analysis->the_domain->functions)
		current_analysis->the_domain->functions->visit(&aa);
    TA = new TIMAnalyser(*theTC,current_analysis);
    current_analysis->the_domain->visit(TA);
    current_analysis->the_problem->visit(TA);
    for_each(current_analysis->the_domain->ops->begin(),
    			current_analysis->the_domain->ops->end(),completeMutexes);
	TA->checkSV();
    dapb.reverse();
    current_analysis->the_domain->visit(&dapb);
    for(vector<durative_action*>::iterator i = aa.getFixedDAs().begin();
    		i != aa.getFixedDAs().end();++i)
    {
    	(static_cast<TIMactionSymbol*>((*i)->name))->assertFixedDuration();
    };
}

};

