#ifndef MOSEK_SOLVER_H_
#define MOSEK_SOLVER_H_

#ifdef USE_MOSEK

#include "LP_solver.h"
#include "LPConstraint.h"
#include "SP_globals.h"
//#pragma GCC diagnostic ignored "-Wlong-long"
#include "mosek.h"


class MOSEK_solver: public LP_solver {

	MSKenv_t env;
	MSKboundkeye *bkx;
	double *blx;
	double *bux;
	double *c;
	MSKlidxt *ptrb;
	MSKlidxt *ptre;
	MSKboundkeye *bkc;
	double *blc;
	double *buc;

	MSKidxt *asub;
	double *aval;

	int cols,rows,nonzeros;

	void create_MOSEK_objective(vector<ConstraintVar*>& obj_func);
	void create_MOSEK_matrix(vector<LPConstraint*> &constr);
	double solve_MOSEK_task(MSKtask_t &task, MSKrealt * xx);

	void dump_MOSEK_data();

public:
	MOSEK_solver();
	virtual ~MOSEK_solver();

	virtual void initialize();
	virtual void free_mem();

	virtual void set_size(int n_cols, int n_rows, int n_nonzeros);

	virtual double solve(vector<ConstraintVar*>& obj_func, vector<LPConstraint*>& constr, Solution* sol);

};
#endif
#endif /* MOSEK_SOLVER_H_ */
