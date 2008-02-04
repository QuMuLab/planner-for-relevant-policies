#ifndef __TIMUTILS
#define __TIMUTILS

#include <iostream>
#include <iterator>


using std::ostream;
using std::iterator;

namespace VAL {
class pddl_type;
};

template<class T>
struct ptrwriter
{
	ostream & os;
	char * septr;
	
	ptrwriter(ostream & o,char * sep) : os(o), septr(sep) {};
	void operator()(T * p)
	{
		os << (*p) << septr;
	};
};

namespace TIM {

template<class TI>
struct typeTransformer : 
	public 
#ifndef OLDCOMPILER
			std::iterator
#endif
#ifdef OLDCOMPILER
			std::forward_iterator
#endif
					<typename std::iterator_traits<TI>::iterator_category,VAL::pddl_type *>{
	TI ti;
	int arg;
	const VAL::pddl_type * pt;
	int cnt;

	typeTransformer(TI t,int a,const VAL::pddl_type * p) :
		ti(t), arg(a), pt(p), cnt(0) {};

	VAL::pddl_type * operator*() 
	{
		if(cnt==arg) return const_cast<VAL::pddl_type *>(pt);
		return (*ti)->type;
	};
	typeTransformer<TI> & operator++() {++ti; ++cnt; return *this;};
	bool operator==(const typeTransformer<TI> & t) const {return ti == t.ti;};
	size_t operator-(const typeTransformer<TI> & t) const
	{
		return ti - t.ti;
	};
};

template<class TI>
typeTransformer<TI> makeTT(TI t,int a,const VAL::pddl_type * p)
{
	return typeTransformer<TI>(t,a,p);
};

};

#endif
