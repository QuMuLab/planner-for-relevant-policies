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

#ifndef __VALUTILS
#define __VALUTILS

using std::ostringstream;
using std::string;

namespace VAL {
  
template <typename T>
struct ToStringer {
	string operator()(T d)
	{
		ostringstream aStringStream;
		aStringStream << d;
		return aStringStream.str();
	};
};

template <typename T>
struct ToStringer<T *> {
	string operator()(T * d)
	{
		ostringstream aStringStream;
		aStringStream << *d;
		return aStringStream.str();
	};
};

template<typename T>
string toString(T d)
{
	ToStringer<T> ts;
	return ts(d);
};

void replaceSubStrings(string & s,string s1,string s2);

void latexString(string & s);

};

#endif
