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
#ifndef SIM__EXCEPTIONS
#define SIM__EXCEPTIONS
#include <exception>
using std::exception;

namespace VAL {
  
struct UndefinedPolyError : public exception {

	const char * what() const throw()
	{
		return "Attempt to access undefined polynomial!";
	};

};

struct HighOrderDiffEqunError : public exception {

	const char * what() const throw()
	{
		return "Higher order differential equations of this nature are not handled!";
	};
};

struct DiffEqunError : public exception {

	const char * what() const throw()
	{
		return "Differential equations of this nature are not handled!";
	};
};

struct NumError : public exception {

	const char * what() const throw()
	{
		return "Numerical error in calculation of Primitive Numerical Values!";
	};
};

struct InfiniteRootsError : public exception {

	const char * what() const throw()
	{
		return "Attempt to find roots of constant value zero!";
	};
};

struct PolyRootError : public exception {

	const char * what() const throw()
	{
		return "The roots of this polynomial cannot be found!";
	};
};

struct ApproxPolyError : public exception {

	const char * what() const throw()
	{
		return "An approximate polynomial to this continuous function cannot be found!";
	};
};

struct InvariantError : public exception {

	const char * what() const throw()
	{
		return "This validator cannot handle invariants of this nature!";
	};
};

struct InvariantDisjError : public exception {

	const char * what() const throw()
	{
		return "The intervals satisfying a disjunct of an invariant cannot be found!";
	};
};

struct InvalidIntervalsError : public exception {

	const char * what() const throw()
	{
		return "This collection of intervals is invalid!";
	};
};

struct DerivedPredicateError : public exception {

	const char * what() const throw()
	{
		return "Problem with derived predicates!";
	};
};

struct TemporalDAError : public exception {

	const char * what() const throw()
	{
		return "Conditional effects cannot depend on future events!";
	};
};

struct BadOperator : public exception {

	const char * what() const throw()
	{
		return "Bad operator in plan!";
	};
};

struct SyntaxTooComplex : public exception {

	const char * what() const throw()
	{
		return "Syntax not handled by this validator!";
	};
};

struct UnrecognisedCondition : public exception {

	const char * what() const throw()
	{
		return "Unrecognised exception - unexpected situation!";
	};
};

struct BadAccessError : public exception {

	const char * what() const throw()
	{
		return "Attempt to access undefined numeric expression!";
	};
};

struct ParseFailure : public exception {

	const char * what() const throw()
	{
		return "Parser failed to read file!\n";
	};
};

struct TypeException : public exception {

	const char * what() const throw()
	{
		return "Error in type-checking!\n";
	};
};

};

#endif
