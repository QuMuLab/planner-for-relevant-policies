#ifndef OSI_SOLVER_H_
#define OSI_SOLVER_H_

#ifdef USE_OSI
#pragma GCC diagnostic ignored "-Wunused-parameter"
#ifdef COIN_USE_CLP
#include "OsiClpSolverInterface.hpp"
typedef OsiClpSolverInterface OsiXxxSolverInterface;
#endif

#ifdef COIN_USE_MSK
#include "OsiMskSolverInterface.hpp"
typedef OsiMskSolverInterface OsiXxxSolverInterface;
#endif

#ifdef COIN_USE_OSL
#include "OsiOslSolverInterface.hpp"
typedef OsiOslSolverInterface OsiXxxSolverInterface;
#include "ekk_c_api.h"
#endif

#ifdef COIN_USE_CPX
#include "OsiCpxSolverInterface.hpp"
typedef OsiCpxSolverInterface OsiXxxSolverInterface;
#endif

#include "CoinPackedVector.hpp"
#include "CoinPackedMatrix.hpp"
#include <sys/times.h>

#include "LP_solver.h"
#include "LPConstraint.h"
#include "SP_globals.h"
//#pragma GCC diagnostic ignored "-Wlong-long"


class OSI_solver: public LP_solver {

    OsiXxxSolverInterface* si;
    CoinPackedMatrix * matrix;
    CoinPackedVectorBase ** added_rows;

	int cols,rows,nonzeros;
    double * objective ;//the objective coefficients
    double * col_lb;//the column lower bounds
    double * col_ub;//the column upper bounds
    double * row_lb; //the row lower bounds
    double * row_ub; //the row upper bounds

	void create_OSI_objective(vector<ConstraintVar*>& obj_func);
	void create_OSI_matrix(vector<LPConstraint*> &constr);
	void dump();

public:
	OSI_solver();
	virtual ~OSI_solver();

	virtual void initialize();
	virtual void free_mem();

	virtual void set_size(int n_cols, int n_rows, int );

	virtual double solve(vector<ConstraintVar*>& obj_func, vector<LPConstraint*>& constr, Solution* sol);

};
#endif
#endif /* OSI_SOLVER_H_ */
