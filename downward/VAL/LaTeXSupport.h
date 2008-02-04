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

#ifndef __LATEXSUPPORT
#define __LATEXSUPPORT

#include <vector>
#include <string>
#include <iostream>
#include "Utils.h"
#include "main.h"
#include "Validator.h"


using std::ostream;
using std::string;
using std::vector;

namespace VAL {
  
struct showList {
	void operator()(const pair<double,vector<string> > & ps) const
	{
		if(LaTeX)
		{		
			string s;
			*report << ps.first<<" \\>";
			for(vector<string>::const_iterator i = ps.second.begin(); i != ps.second.end() ; ++i)
			{
				s = *i; 
				replaceSubStrings(s,"/","/\\-");
            	latexString(s);
				*report << "\\begin{minipage}[t]{12cm} " << s << " \\end{minipage}\\\\\n \\>";
			};
			*report << "\\\\\n";
		}
		else
		{
			cout << "\nValue: " << ps.first << "\n ";
			copy(ps.second.begin(),ps.second.end(),ostream_iterator<string>(cout," "));
			cout << "\n";
		};
	};
};

void displayFailedLaTeXList(vector<string> & vs);

class LaTeXSupport {
private:
	int NoGraphPoints;
	int noPoints;
	int noGCPages;
	int noGCPageRows;
	vector<string> ganttObjectsAndTypes;
	vector<string> ganttObjects;
public:
	LaTeXSupport() : NoGraphPoints(500), noGCPages(0), noGCPageRows(0) {};
	void LaTeXHeader();
	void LaTeXPlanReportPrepare(char *);
	void LaTeXPlanReport(Validator * v,plan *);
	void LaTeXEnd();
	void LaTeXGantt(Validator * v);
	void LaTeXGraphs(Validator * v);
	void LaTeXDomainAndProblem();
	void LaTeXBuildGraph(ActiveCtsEffects * ace,const State * s);
	void setnoGCPages(int g) {noGCPages = g;};
	void setnoGCPageRows(int g) {noGCPageRows = g;};
	void setnoPoints(int n)
	{
		noPoints = n;
		if(noPoints < 10) noPoints = 10;
		else if(noPoints > 878) noPoints = 878;
	    NoGraphPoints = noPoints;
	};
	void addGanttObject(char * c)
	{
		ganttObjectsAndTypes.push_back(c);
	};
};

extern LaTeXSupport latex;

};



#endif
