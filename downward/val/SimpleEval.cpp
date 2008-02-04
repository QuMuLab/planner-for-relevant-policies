#include "SimpleEval.h"
#include "TypedAnalyser.h"

using namespace VAL;

namespace Inst {

IState SimpleEvaluator::initState;
IState0Arity SimpleEvaluator::init0State;

void SimpleEvaluator::visit_preference(preference * p)
{};

void SimpleEvaluator::setInitialState()
{
	initState.clear();
	init0State.clear();
	
	for(pc_list<simple_effect*>::const_iterator i = 
				current_analysis->the_problem->initial_state->add_effects.begin();
				i != current_analysis->the_problem->initial_state->add_effects.end();++i)
	{
		if((*i)->prop->args->begin()==(*i)->prop->args->end())
		{
			// Arity 0...
			init0State.insert((*i)->prop->head);

		}
		else
		{
			initState[(*i)->prop->head].push_back((*i)->prop->args);
		};
	};
};

bool partialMatch(const const_symbol * x,const const_symbol * y)
{
	return x==y || x==0 || y==0;
};

bool SimpleEvaluator::equiv(const parameter_symbol_list * s,const parameter_symbol_list * p)
{
	parameter_symbol_list::const_iterator y = p->begin();
	for(parameter_symbol_list::const_iterator x = s->begin();x != s->end();++x,++y)
	{
		if((*f)[*x] != *y) return false;
	};
	return true;
};
					
void SimpleEvaluator::visit_simple_goal(simple_goal * s)
{
	if(EPS(s->getProp()->head)->getParent() == this->equality)
	{
//	cout << "Got equality\n";
		unknown = false;
		if(!partialMap) 
		{
			value = ((*f)[s->getProp()->args->front()] == 
						(*f)[s->getProp()->args->back()]);
		}
		else
		{
			value = partialMatch((*f)[s->getProp()->args->front()],
						(*f)[s->getProp()->args->back()]);
		};
		if(s->getPolarity() == E_NEG)
		{
			value = !value;
		};
		return;
	};
	extended_pred_symbol * eps = EPS(s->getProp()->head);
	if(eps->appearsStatic())
	{
		if(!eps->isCompletelyStatic(f,s->getProp()))
		{
//			cout << s->getProp()->head->getName() << " is a faker\n";
			unknown = true;
			return;
		};
		
		unknown = false;
		
		if(!partialMap && EPS(s->getProp()->head)->
				contains(f,s->getProp()) || 
				partialMap && EPS(s->getProp()->head)->partContains(f,s->getProp()))
		{
			value = true;
			return;
		}; 
		value = (init0State.find(s->getProp()->head) != init0State.end());
		if(s->getPolarity() == E_NEG)
		{
			value = !value;
		};
	}
	else unknown = true;
};

void SimpleEvaluator::visit_qfied_goal(qfied_goal * q)
{
	for(var_symbol_list::const_iterator i = q->getVars()->begin();
			i != q->getVars()->end();++i)
	{
		cout << "Got: " << static_cast<const IDsymbol<var_symbol> *>(*i)->getId() << "\n";
	};
// For the moment it is easier to treat this as unknown...
	unknown = true;
};

void SimpleEvaluator::visit_conj_goal(conj_goal * c)
{
	bool u = false;
	value = true;
	for(goal_list::const_iterator i = c->getGoals()->begin();
		i != c->getGoals()->end();++i)
	{
		(*i)->visit(this);
		if(reallyFalse()) return;
		u = u || unknown;
	};
	unknown = u;
};
	
void SimpleEvaluator::visit_disj_goal(disj_goal * d)
{
	for(goal_list::const_iterator i = d->getGoals()->begin();
		i != d->getGoals()->end();++i)
	{
		(*i)->visit(this);
		if(!reallyFalse()) return;
	};
};

void SimpleEvaluator::visit_timed_goal(timed_goal * t)
{
	t->getGoal()->visit(this);
};

void SimpleEvaluator::visit_imply_goal(imply_goal * ig)
{
	ig->getAntecedent()->visit(this);
	if(unknown) return;
	if(value)
	{
		ig->getConsequent()->visit(this);
	}
	else value = true;
};

void SimpleEvaluator::visit_neg_goal(neg_goal * ng)
{
	ng->getGoal()->visit(this);
	if(!unknown)
	{
		value = !value;
	};
};

void SimpleEvaluator::visit_event(event * op)
{
	op->precondition->visit(this);
};

void SimpleEvaluator::visit_process(process * op)
{
	op->precondition->visit(this);
};


void SimpleEvaluator::visit_comparison(comparison * c)
{
//	unknown = true;
//	return;
	
	isFixed = false;
	undefined = false;
	isDuration = false;
	c->getLHS()->visit(this);
	if(undefined) 
	{
		unknown = false;
		value = false;
		return;
	};
	bool lhsFixed = isFixed;
	double lhsval = nvalue;
	bool lhsDur = isDuration;
	isDuration = false;
	c->getRHS()->visit(this);
	if(undefined)
	{
		unknown = value = false;
		return;
	};
	if(lhsDur)
	{
		value = true;
		unknown = false;
		return;
	};
	isFixed &= lhsFixed;
	if(isFixed)
	{
		unknown = false;
		switch(c->getOp())
		{
			case E_GREATER:
				value = (lhsval > nvalue);  // I think this is a problem case if 
											// we are comparing with ?duration in the
											// special duration field.... 
				break;
			case E_GREATEQ:
				value = (lhsval >= nvalue);
				break;
			case E_LESS:
				value = (lhsval < nvalue);
				break;
			case E_LESSEQ:
				value = (lhsval <= nvalue);
				break;
			default: // E_EQUALS
				value = (lhsval == nvalue);
		};
	}
	else
	{
		unknown = true;
	};
};

void SimpleEvaluator::visit_action(action * op)
{
	op->precondition->visit(this);
};

void SimpleEvaluator::visit_durative_action(durative_action * da)
{
	da->precondition->visit(this);
	if(unknown || value)
	{
		da->dur_constraint->visit(this);
	};
};



void SimpleEvaluator::visit_plus_expression(plus_expression * s)
{
	s->getLHS()->visit(this);
	double x = nvalue;
	bool lisFixed = isFixed;
	s->getRHS()->visit(this);
	nvalue += x;
	isFixed &= lisFixed;
};

void SimpleEvaluator::visit_minus_expression(minus_expression * s)
{
	s->getLHS()->visit(this);
	double x = nvalue;
	bool lisFixed = isFixed;
	s->getRHS()->visit(this);
	nvalue -= x;
	isFixed &= lisFixed;
};

void SimpleEvaluator::visit_mul_expression(mul_expression * s)
{
	s->getLHS()->visit(this);
	double x = nvalue;
	bool lisFixed = isFixed;
	s->getRHS()->visit(this);
	nvalue *= x;
	isFixed &= lisFixed;
};

void SimpleEvaluator::visit_div_expression(div_expression * s)
{
	s->getLHS()->visit(this);
	double x = nvalue;
	bool lisFixed = isFixed;
	s->getRHS()->visit(this);
	isFixed &= lisFixed;
	if(x != 0)
	{
		nvalue /= x;
	};
	if(isFixed && x == 0)
	{
		undefined = true;
	};
};

void SimpleEvaluator::visit_uminus_expression(uminus_expression * s)
{
	s->getExpr()->visit(this);
};

void SimpleEvaluator::visit_int_expression(int_expression * s)
{
	isFixed = true;
	nvalue = s->double_value();
};

void SimpleEvaluator::visit_float_expression(float_expression * s)
{
	isFixed = true;
	nvalue = s->double_value();
};

void SimpleEvaluator::visit_special_val_expr(special_val_expr * s)
{
	if(s->getKind() == E_DURATION_VAR) isDuration = true;
	isFixed = true; // Possibly inappropriate...
};

void SimpleEvaluator::visit_func_term(func_term * s)
{
	extended_func_symbol * efs = EFT(s->getFunction());
	//cout << "Eval: " << s->getFunction()->getName() << "\n";
	if(efs->isStatic())
	{
		isFixed = true;
		pair<bool,double> pv = efs->getInitial(makeIterator(f,s->getArgs()->begin()),
						makeIterator(f,s->getArgs()->end()));
		if(pv.first)
		{
			nvalue = pv.second;
			//cout << "Value is " << nvalue << "\n";
		}
		else
		{
			undefined = true;
			//cout << "Undefined\n";
		};
	}
	else
	{
		isFixed = false;
		//cout << "Variable\n";
	};
};

};
