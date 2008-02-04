#ifndef __SIMPLE_EVALUATOR
#define __SIMPLE_EVALUATOR
#include "VisitController.h"
#include "FastEnvironment.h"
#include <map>
#include <vector>
#include <set>
#include "ptree.h"

namespace Inst {

typedef std::set<VAL::pred_symbol *> IState0Arity;
typedef std::map<VAL::pred_symbol *,vector<VAL::parameter_symbol_list*> > IState;

class SimpleEvaluator : public VAL::VisitController {
protected:
	bool value;
	bool unknown;
	VAL::FastEnvironment * f;
	bool partialMap;

	VAL::pred_symbol * equality;
	
	static IState initState;
	static IState0Arity init0State;

	bool isFixed;
	bool undefined;
	double nvalue; // Used for numeric values.
	bool isDuration;
	
public:

	static void setInitialState();
	
	SimpleEvaluator(VAL::FastEnvironment * ff) : value(true), unknown(false), f(ff),
		partialMap(false), equality(VAL::current_analysis->pred_tab.symbol_probe("=")) {};
	bool reallyTrue() const
	{
		return !unknown && value;
	};
	bool reallyFalse() const
	{
		return !unknown && !value;
	};

	
	virtual void visit_simple_goal(VAL::simple_goal *);
	virtual void visit_qfied_goal(VAL::qfied_goal *);
	virtual void visit_conj_goal(VAL::conj_goal *);
	virtual void visit_disj_goal(VAL::disj_goal *);
	virtual void visit_timed_goal(VAL::timed_goal *);
	virtual void visit_imply_goal(VAL::imply_goal *);
	virtual void visit_neg_goal(VAL::neg_goal *);
	virtual void visit_comparison(VAL::comparison *);
	virtual void visit_preference(VAL::preference *);
	virtual void visit_event(VAL::event * e);
    virtual void visit_process(VAL::process * p);
	virtual void visit_action(VAL::action * o);
	virtual void visit_durative_action(VAL::durative_action * da);
	void setPartialMaps() {partialMap = true;};
	bool equiv(const VAL::parameter_symbol_list *,const VAL::parameter_symbol_list *);

	virtual void visit_plus_expression(VAL::plus_expression * s);
	virtual void visit_minus_expression(VAL::minus_expression * s);
	virtual void visit_mul_expression(VAL::mul_expression * s);
	virtual void visit_div_expression(VAL::div_expression * s);
	virtual void visit_uminus_expression(VAL::uminus_expression * s);
	virtual void visit_int_expression(VAL::int_expression * s);
	virtual void visit_float_expression(VAL::float_expression * s);
	virtual void visit_special_val_expr(VAL::special_val_expr * s);
	virtual void visit_func_term(VAL::func_term * s);



};

};

#endif
