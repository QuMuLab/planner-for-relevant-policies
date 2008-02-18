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
#include <sstream>
#include <string>
#include "Polynomial.h"
#include "Action.h"
#include "FuncExp.h"
#include "Utils.h"

namespace VAL {
  
void replaceSubStrings(string & s,string s1,string s2)
{
	size_t pos = s.find(s1);
	size_t subPos = pos;
	size_t size = s.size();
	
	
 	for(size_t count = 1;count < size ; ++count)
 	{
		if(subPos != string::npos)
			s.replace(pos,s1.size(),s2);
		else
			break;

		subPos = (s.substr(pos + s2.size(),string::npos)).find(s1);
		pos = pos + s2.size() + subPos;
	};
	
};

//change any action names etc that LaTeX will not like
void latexString(string & s)
{
	replaceSubStrings(s,"_","\\_");
	

};

};
