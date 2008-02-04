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
 
#include <vector>
#include <map>
//#include "Validator.h"
//#include "random.h"
#include "ptree.h"

#ifndef __ROBUSTANALYSE
#define __ROBUSTANALYSE

using std::map;
using std::pair;
using std::vector;
using std::make_pair;

namespace VAL {

extern bool Robust;
extern double RobustPNEJudder;
extern bool JudderPNEs;
extern bool EventPNEJuddering;
extern bool TestingPNERobustness;
extern bool LaTeXRecord;

enum RobustMetric{DELAY,ACCUM,MAX};
enum RobustDist{UNIFORM,NORMAL,PNORM};

struct InvalidActionRecord
{
  int number;
  double time;
  plan_step * ps;
  //set<string> failReasons;

  InvalidActionRecord(int no, double t, plan_step * p): number(no), time(t), ps(p) {};
  ~InvalidActionRecord() {};
};

struct InvalidActionReport
{
  int number;
  map<string,pair<int,string> > failReasons;

  InvalidActionReport(): number(0), failReasons() {};
  InvalidActionReport(int no,string r,string a): number(no), failReasons()
  {
    failReasons[r] = make_pair(no,a);  
  };
  ~InvalidActionReport() {};
};

class DerivationRules;
class TypeChecker;

class RobustPlanAnalyser{
private:

  const plan * p;
  vector<plan_step *> timedIntitialLiteralActions;

  double robustMeasure;
  int noTestPlans;

  map<const plan_step *, InvalidActionReport> record;
  int unsatisfiedGoal;
  int unknownErrors;

  double maxTime;
  bool calcPNERobustness;
  bool calcActionRobustness;
  RobustMetric robustMetric;
  RobustDist robustDist;
  
  //all of the following are needed for creating validator objects
	const DerivationRules * derivRules;
	double tolerance;
	TypeChecker & typeC;
	const metric_spec * metric;
	bool stepLength;
	bool durative;
	const operator_list * operators;
	const effect_lists * initialState;
  analysis * current_analysis;
  const goal * theGoal;
   
public:

     RobustPlanAnalyser(double rm,int ntp,const DerivationRules * dr,double tol,TypeChecker & tc,const operator_list * ops,const effect_lists * is,const plan * p1,const metric_spec * m,
					bool lengthDefault,bool isDur,const goal * g,analysis * ca,vector<plan_step *> initLits,bool car,bool cpr,RobustMetric robm,RobustDist robd) :
          p(p1), timedIntitialLiteralActions(initLits),  robustMeasure(rm), noTestPlans(ntp), record(), unsatisfiedGoal(0), unknownErrors(0), maxTime(0),
          calcPNERobustness(cpr),calcActionRobustness(car),robustMetric(robm),robustDist(robd),                  
          derivRules(dr), tolerance(tol), 
          typeC(tc), metric(m), stepLength(lengthDefault), durative(isDur), operators(ops), initialState(is), current_analysis(ca), theGoal(g)
          {};

  ~RobustPlanAnalyser();

  void displayPlan();
  void analyseRobustness();
  void runAnalysis(double & variation,int & numberTestPlans,bool recordFailures,int & numberOfInvalidPlans,int & numberOfErrorPlans,bool allValid,bool latexAdvice);
  void runAnalysisBoundary(double & variation,int & numberTestPlans,bool recordFailures,int & numberOfInvalidPlans,int & numberOfErrorPlans,bool allValid,bool latexAdvice);
  void calculateActionRobustness(double & robustnessOfPlan,double & robustnessBound);
  void calculatePNERobustness(double & robustnessOfPlan,double & robustnessBound);
  void displayAnalysis(int noTestPlans,int numberOfInvalidPlans,int numberOfErrorPlans,double actionRobustnessOfPlan,double actionRobustnessBound,double pneRobustnessOfPlan,double pneRobustnessBound);
  void displayAnalysisLaTeX(int noTestPlans,int numberOfInvalidPlans,int numberOfErrorPlans,double actionRobustnessOfPlan,double actionRobustnessBound,double pneRobustnessOfPlan,double pneRobustnessBound);

  map<const plan_step *,const plan_step *> varyPlanTimestamps(plan * aplan,const plan * p,double & variation);
  map<const plan_step *,const plan_step *> varyPlanTimestampsDelay(plan * aplan,const plan * p,double & variation);
  map<const plan_step *,const plan_step *> varyPlanTimestampsAccum(plan * aplan,const plan * p,double & variation);
  map<const plan_step *,const plan_step *> varyPlanTimestampsMax(plan * aplan,const plan * p,double & variation);
  map<const plan_step *,const plan_step *> varyPlanTimestampsBoundary(plan * aplan,const plan * p,double & variation,int runNo);
  map<const plan_step *,const plan_step *> varyPlanTimestampsBoundaryDelay(plan * aplan,const plan * p,double & variation,int runNo);
  map<const plan_step *,const plan_step *> varyPlanTimestampsBoundaryAccum(plan * aplan,const plan * p,double & variation,int runNo);
  map<const plan_step *,const plan_step *> varyPlanTimestampsBoundaryMax(plan * aplan,const plan * p,double & variation,int runNo);

  string getMetricName();
  
  double getRandomNumber();
  double getRandomNumberUni();
  double getRandomNumberNorm();
  double getRandomNumberPsuedoNorm();
  string getDistName();

 
};

plan * newTestPlan(const plan * p);
void deleteTestPlan(plan * p);


};


#endif
