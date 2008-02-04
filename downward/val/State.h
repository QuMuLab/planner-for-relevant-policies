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
#include "Proposition.h"
#include "FuncExp.h"
#include<set>
using std::set;

namespace VAL {
class Validator;
class Happening;
};

#ifndef __STATE
#define __STATE

namespace VAL {
  
typedef long double FEScalar;

typedef map<const SimpleProposition*,bool> LogicalState;
typedef map<const FuncExp*,FEScalar> NumericalState;


class State {
private:
	const double tolerance;

	Validator * const vld;

	LogicalState logState;
	NumericalState feValue;
	
	double time;

   //record which literals and PNEs have changed by appliaction of an happening (for triggering events)
   set<const SimpleProposition *> changedLiterals;
   set<const FuncExp *> changedPNEs;
 	 FEScalar evaluateFE(const FuncExp * fe) const;
   
public:
	State(Validator * const v,const effect_lists* is);
	State & operator=(const State & s);

  friend class FuncExp;
	const double getTolerance() const {return tolerance;};
	Validator * getValidator() const {return vld;};
	double getTime() const {return time;};
	
	bool progress(const Happening * h);
  bool progressCtsEvent(const Happening * h);
	bool evaluate(const SimpleProposition * p) const;
	FEScalar evaluate(const FuncExp * fe) const;
	FEScalar evaluate(const expression * e,const Environment & bs) const;

	void add(const SimpleProposition *);
	void del(const SimpleProposition *);
	void update(const FuncExp * fe,assign_op aop,FEScalar value);

	const LogicalState & getLogicalState() const {return logState;};
   //to also record what has changed
  	void addChange(const SimpleProposition *);
	void delChange(const SimpleProposition *);
	void updateChange(const FuncExp * fe,assign_op aop,FEScalar value);
   set<const SimpleProposition *> getChangedLiterals() const {return changedLiterals;};
   set<const FuncExp *> getChangedPNEs() const {return changedPNEs;};
   void resetChanged() {changedLiterals.clear(); changedPNEs.clear();};

	void setNew(const effect_lists * effs);

	void write(ostream & o) const
	{
		for(LogicalState::const_iterator i = logState.begin();i != logState.end();++i)
		{
			if(i->second) o << *(i->first) << "\n";
		};
		for(NumericalState::const_iterator i = feValue.begin();i != feValue.end();++i)
		{
			o << *(i->first) << " = " << i->second << "\n";
		};
	};

	//	friend class const_iterator;

	class const_iterator {
	private:
		const State & st;
		LogicalState::const_iterator it;
	public:
		const_iterator(const State & s) : st(s), it(st.logState.begin())
		{
			while(it != st.logState.end() && !it->second) ++it;
		};
		
		bool operator==(const const_iterator & itr) const
		{
			return it == itr.it;
		};

		bool operator!=(const const_iterator & itr) const
		{
			return it != itr.it;
		};

		const_iterator & operator++()
		{
			++it;
			while(it != st.logState.end() && !it->second) ++it;
			return *this;
		};

		const SimpleProposition * operator*() const
		{
			return it->first;
		};

		void toEnd()
		{
			it = st.logState.end();
		};
	};

	const_iterator begin() const {return const_iterator(*this);};
	const_iterator end() const {const_iterator ci(*this); ci.toEnd(); return ci;};
};

inline ostream & operator<<(ostream & o,const State & s)
{
	s.write(o);
	return o;
};


};

#endif
