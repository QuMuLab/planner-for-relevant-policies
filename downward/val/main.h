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
#ifndef __MAIN
#define __MAIN

#include <iostream>
using std::ostream;

namespace VAL {
  
extern bool Verbose;
extern bool ContinueAnyway;
extern bool ErrorReport;
extern bool InvariantWarnings;
extern bool LaTeX;
extern bool LaTeXRecord;
extern ostream*report;
extern int NoGraphPoints;
extern bool makespanDefault;


};

#endif
