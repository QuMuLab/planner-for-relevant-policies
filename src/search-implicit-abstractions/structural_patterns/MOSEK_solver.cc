#ifdef USE_MOSEK

#include "MOSEK_solver.h"
#include <math.h>
#include "../globals.h"
#include <cfloat>

MOSEK_solver::MOSEK_solver() {

	bkx = NULL;
	blx = NULL;
	bux = NULL;
	c = NULL;
	ptrb = NULL;
	ptre = NULL;
	bkc = NULL;
	blc = NULL;
	buc = NULL;

	asub = NULL;
	aval = NULL;

	cols = 0;
	rows = 0;
	nonzeros = 0;

	MSKrescodee r;

	// Create the mosek environment.
	r = MSK_makeenv(&env,NULL,NULL,NULL,NULL);
	if ( r!=MSK_RES_OK ) {
		cout << "Problem with creating environment" << endl;
		exit(0);
	}
	// Initialize the environment.
	r = MSK_initenv(env);
	if ( r!=MSK_RES_OK ) {
		cout << "Problem with initializing environment" << endl;
		exit(0);
	}
}

MOSEK_solver::~MOSEK_solver() {
	MSK_deleteenv(&env);
	free_mem();
}

void MOSEK_solver::set_size(int n_cols, int n_rows, int n_nonzeros){
	cols = n_cols;
	rows = n_rows;
	nonzeros = n_nonzeros;

}

void MOSEK_solver::initialize(){

//	if ((LP_cost_partitioning == GENERAL) && (STATISTICS>=1)) {
//		cout << "Initializing LP with "<< cols << " variables and " << rows << " constraints, and " <<  nonzeros << " nonzeros." << endl;
//	}
	bkx = new MSKboundkeye[cols];
	blx = new double[cols];
	bux = new double[cols];
	c = new double[cols];

	ptrb = new MSKlidxt[cols];
	ptre = new MSKlidxt[cols];

	bkc = new MSKboundkeye[rows];
	blc = new double[rows];
	buc = new double[rows];

	asub = new MSKidxt[nonzeros];
	aval = new double[nonzeros];

}

void MOSEK_solver::free_mem(){

	if (ptrb) {
		delete [] ptrb;
		ptrb = NULL;
	}
	if (ptre) {
		delete [] ptre;
		ptre = NULL;
	}

	if (bkc) {
		delete [] bkc;
		bkc = NULL;
	}
	if (blc) {
		delete [] blc;
		blc = NULL;
	}
	if (buc) {
		delete [] buc;
		buc = NULL;
	}

	if (asub) {
		delete [] asub;
		asub = NULL;
	}
	if (aval) {
		delete [] aval;
		aval = NULL;
	}

	if (bkx) {
		delete [] bkx;
		bkx = NULL;
	}
	if (blx) {
		delete [] blx;
		blx = NULL;
	}
	if (bux) {
		delete [] bux;
		bux = NULL;
	}
	if (c) {
		delete [] c;
		c = NULL;
	}

}

double MOSEK_solver::solve(vector<ConstraintVar*>& obj_func, vector<LPConstraint*>& constr, Solution* sol) {
	MSKrealt *xx = NULL;
	if (sol) {
		xx = new MSKrealt[cols];
	}
	create_MOSEK_objective(obj_func);
	create_MOSEK_matrix(constr);

	MSKtask_t task;
	MSKrescodee r;

	// Create the optimization task.
	r = MSK_maketask(env,rows,cols,&task);
	if ( r!=MSK_RES_OK ) {
		cout << "Problem with creating task" << endl;
		exit(0);
	}
	double val = solve_MOSEK_task(task, xx);

	MSK_deletetask(&task);
	if (sol) {
		sol->set_solution(xx,cols);
		delete xx;
	}

	return val;
}

void MOSEK_solver::create_MOSEK_objective(vector<ConstraintVar*>& obj_func) {

	// Fill the objectives and variable bounds - [0,inf)
	for (int i =0; i < cols; i++) {
		c[i] = 0.0;
		bkx[i] = MSK_BK_RA;
		blx[i] = 0.0;
		bux[i] = LP_INFINITY;
		//bkx[i] = MSK_BK_LO;
		//bux[i] = +MSK_INFINITY;
	}

	for (int i =0; i < obj_func.size(); i++) {
		c[obj_func[i]->var] = obj_func[i]->val;
	}
}

void MOSEK_solver::create_MOSEK_matrix(vector<LPConstraint*> &constr) {

	for (int i=0;i<cols;i++) {
		ptre[i] = 0;
	}

	for (int i=0;i<rows;i++) {
		vector<ConstraintVar*> cvars = constr[i]->get_vals();
		int nonz = cvars.size();
		int index = constr[i]->get_index();
		for (int j =0; j < nonz;j++) {
			int ind = cvars[j]->var + index;
			ptre[ind]++;
		}
	}

	int m_vars = 0;
	for (int i=0;i<cols;i++) {
		if (ptre[i] > 0)
			m_vars++;
	}

//	if (STATISTICS>=1) {
//		cout << "Initializing LP with "<< m_vars << " variables and " << rows << " constraints, and " <<  nonzeros << " nonzeros." << endl;
//	}

	int* ptr = new int[cols];
	ptrb[0] = 0;
	ptr[0] = 0;
	for (int i=1;i<cols;i++) {
		ptre[i] += ptre[i-1];
		ptrb[i] = ptre[i-1];
		ptr[i] = ptre[i-1];
	}

	for (int i=0;i<rows;i++) {
		vector<ConstraintVar*> cvars = constr[i]->get_vals();
		int index = constr[i]->get_index();
		int nonz = cvars.size();
		for (int j =0; j < nonz;j++) {
			int ind = cvars[j]->var + index;
			asub[ptr[ind]] = i;
			aval[ptr[ind]] = cvars[j]->val;
			ptr[ind]++;
		}

		// For now our constraints are only of following types,
		// In case it changes, we should add cases
		double lb = constr[i]->get_lb();
		double ub = constr[i]->get_ub();

		if (lb == ub) { // For equality
			bkc[i] = MSK_BK_FX;
			blc[i] = lb;
			buc[i] = ub;
			continue;
		}
		if (ub == DBL_MAX) {
			if (lb == -DBL_MAX) {   // For (-INF,INF)
				bkc[i] = MSK_BK_FR;
				blc[i] = -MSK_INFINITY;
				buc[i] = +MSK_INFINITY;
				continue;
			}						// For [l,INF)
			bkc[i] = MSK_BK_LO;
			blc[i] = lb;
			buc[i] = +MSK_INFINITY;
			continue;
		}
		if (lb == -DBL_MAX) {  // For (-INF,u]
			bkc[i] = MSK_BK_UP;
			blc[i] = -MSK_INFINITY;
			buc[i] = ub;
			continue;
		}
		// For [l,u]
		bkc[i] = MSK_BK_RA;
		blc[i] = lb;
		buc[i] = ub;
	}
	delete [] ptr;
}


double MOSEK_solver::solve_MOSEK_task(MSKtask_t &task, MSKrealt * xx) {

	double pobj;
	double dobj;

	MSKrescodee r;

	MSKprostae prosta;
	MSKsolstae solsta;

	r = MSK_inputdata(task,rows,cols,rows,cols,c,0.0,ptrb,ptre,asub,aval,bkc,blc,buc,bkx,blx,bux);
	if ( r!=MSK_RES_OK ) {
		dump_MOSEK_data();
		exit(0);
	}
	MSK_putobjsense(task,MSK_OBJECTIVE_SENSE_MAXIMIZE);

//	MSK_putintparam(task,MSK_IPAR_OPTIMIZER,MSK_OPTIMIZER_INTPNT);   // Interior point
	MSK_putdouparam(task,MSK_DPAR_OPTIMIZER_MAX_TIME,LP_MAX_TIME_BOUND);
	MSK_putintparam(task,MSK_IPAR_OPTIMIZER,MSK_OPTIMIZER_FREE_SIMPLEX); // Simplex
//	MSK_putintparam(task,MSK_IPAR_OPTIMIZER,MSK_OPTIMIZER_CONCURRENT);
//	MSK_putintparam(task,MSK_IPAR_CONCURRENT_NUM_OPTIMIZERS,3);
//	MSK_writedata(task, "test.lp");

//	MSK_writedata(task, (char *) "test.lp");
	r = MSK_optimize(task);
	if ( r!=MSK_RES_OK ) {
		cout << "Problems with optimizing: " << r << endl;
		MSK_writedata(task, (char *) "test.lp");
//		exit(1);
		// TODO: code for problem with optimizing
		return 0.0;
	}
	r = MSK_getsolutioninf(task,MSK_SOL_BAS,&prosta,&solsta,&pobj,NULL,NULL,NULL,NULL,&dobj,NULL,NULL,NULL);

	if ((solsta == MSK_SOL_STA_OPTIMAL) && (dobj-pobj < 0.01)) {
		if (xx)
			r = MSK_getsolution(task,MSK_SOL_BAS,&prosta,&solsta,NULL,NULL,NULL,NULL,xx,NULL,NULL,NULL,NULL,NULL,NULL);
	} else {
		r = MSK_getsolutioninf(task,MSK_SOL_ITR,&prosta,&solsta,&pobj,NULL,NULL,NULL,NULL,&dobj,NULL,NULL,NULL);
		if ((solsta == MSK_SOL_STA_OPTIMAL) && (dobj-pobj < 0.01)) {
			if (xx)
				r = MSK_getsolution(task,MSK_SOL_ITR,&prosta,&solsta,NULL,NULL,NULL,NULL,xx,NULL,NULL,NULL,NULL,NULL,NULL);
		} else {
			cout << "Solver failed with solution status "<< solsta << endl;
			MSK_writedata(task, (char *) "test.lp");
			return 0.0;
		}
		return pobj;
	}
	return pobj;
}


void MOSEK_solver::dump_MOSEK_data() {
	cout << "Problem with inputting data" << endl;
	cout << "Number of rows : " << rows << ", Number of columns : " << cols << endl;

	cout << "Objective : " << c[0];
	for (int i=1;i<cols;i++)
		cout << ", " << c[i];
	cout << endl << "Ptrb : " << ptrb[0];
	for (int i=1;i<cols;i++)
		cout << ", " << ptrb[i];
	cout << endl << "Ptre : " << ptre[0];
	for (int i=1;i<cols;i++)
		cout << ", " << ptre[i];
	cout << endl << "Asub : " << asub[0];
	for (int i=1;i<nonzeros;i++)
		cout << ", " << asub[i];
	cout << endl << "Aval : " << aval[0];
	for (int i=1;i<nonzeros;i++)
		cout << ", " << aval[i];
	cout << endl << "Bkc : " << bkc[0];
	for (int i=1;i<rows;i++)
		cout << ", " << bkc[i];
	cout << endl << "Blc : " << blc[0];
	for (int i=1;i<rows;i++)
		cout << ", " << blc[i];
	cout << endl << "Buc : " << buc[0];
	for (int i=1;i<rows;i++)
		cout << ", " << buc[i];
	cout << endl << "Bkx : " << bkx[0];
	for (int i=1;i<cols;i++)
		cout << ", " << bkx[i];
	cout << endl << "Blx : " << blx[0];
	for (int i=1;i<cols;i++)
		cout << ", " << blx[i];
	cout << endl << "Bux : " << bux[0];
	for (int i=1;i<cols;i++)
		cout << ", " << bux[i];
	cout << endl;
}
#endif
