/*-----------------------------------------------------------------------------
  VAL - The Automatic Plan Validator for PDDL+

  $Date: 2005/06/07 14:00:00 $
  $Revision: 4 $

  Maria Fox, Richard Howey and Derek Long - PDDL+ and VAL
  Stephen Cresswell - PDDL Parser

  maria.fox@cis.strath.ac.uk
  derek.long@cis.strath.ac.uk
  stephen.cresswell@cis.strath.ac.uk
  richard.howey@cis.strath.ac.uk

  By releasing this code we imply no warranty as to its reliability
  and its use is entirely at your own risk.

  Strathclyde Planning Group
  http://planning.cis.strath.ac.uk
 ----------------------------------------------------------------------------*/
#include "FuncExp.h"
#include "State.h"
#include "random.h"
#include "main.h"
#include "RobustAnalyse.h"

//#define map std::map
namespace VAL {
  
double
FuncExp::evaluate(const State * s) const 
{
  double ans = s->evaluateFE(this);
 
  if(JudderPNEs && hasChangedCtsly)
  {
        ans += RobustPNEJudder*(1-2*getRandomNumberUniform()); //if not robustness testing this change will not be activated    
  };
	return ans;
};

string FuncExp::getParameter(int paraNo) const
{          
      int parameterNo = 1;
		for(parameter_symbol_list::const_iterator i = fe->getArgs()->begin();
				i != fe->getArgs()->end();++i)
		{
         if(paraNo == parameterNo)
         {
         			if(dynamic_cast<const var_symbol *>(*i))
         			{
         				return bindings.find(dynamic_cast<const var_symbol *>(*i))->second->getName();
         			}
         			else

         			{
         				return (*i)->getName();

         			};
         };
         ++parameterNo;

		};
      
  return "";
};

bool FuncExp::checkConstantsMatch(const parameter_symbol_list* psl) const
{
  const_symbol * aConst;

  parameter_symbol_list::const_iterator ps = psl->begin();   //from event
  	for(parameter_symbol_list::const_iterator i = fe->getArgs()->begin(); //from func
  				i != fe->getArgs()->end();++i)
  {
     if(dynamic_cast<const const_symbol*>(*ps))
     {

       if(const var_symbol * aVariable = dynamic_cast<const var_symbol *>(*i))
       {
            aConst = const_cast<const_symbol*>(bindings.find(aVariable)->second);
       }
       else
       {
            aConst = const_cast<const_symbol*>(dynamic_cast<const const_symbol*>(*i));
       };

       if(*ps != aConst) return false;
     };

     ++ps;
  };

  return true;
};

ostream & operator <<(ostream & o,const FuncExp & fe) 
{
	fe.write(o);
	return o;
};

void FuncExp::setChangedCtsly()
{ 
 hasChangedCtsly = true;
};

Environment FuncExpFactory::nullEnv;

FuncExpFactory::~FuncExpFactory()
{
	for(map<string,const FuncExp*>::const_iterator i = funcexps.begin();i != funcexps.end();++i)
		delete const_cast<FuncExp*>(i->second);
};

};
