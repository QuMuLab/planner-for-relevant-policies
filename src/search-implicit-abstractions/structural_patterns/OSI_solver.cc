#ifdef USE_OSI

#include "OSI_solver.h"
#include <math.h>
#include "../globals.h"
#include <cfloat>

OSI_solver::OSI_solver() {

	// Create the OSI environment.
    si = new OsiXxxSolverInterface();


	cols = 0;
	rows = 0;
	nonzeros = 0;


}

OSI_solver::~OSI_solver() {
    delete si;
	free_mem();
}

void OSI_solver::set_size(int n_cols, int n_rows, int n_nonzeros){
	cols = n_cols;
	rows = n_rows;
	nonzeros = n_nonzeros;

}

void OSI_solver::initialize(){

//	if ((LP_cost_partitioning == GENERAL) && (STATISTICS>=1)) {
//		cout << "Initializing LP with "<< cols << " variables and " << rows << " constraints, and " <<  nonzeros << " nonzeros." << endl;
//	}

    objective    = new double[cols];//the objective coefficients
    col_lb       = new double[cols];//the column lower bounds
    col_ub       = new double[cols];//the column upper bounds
}

void OSI_solver::free_mem(){

    //free the memory
	if(objective != NULL)   { delete [] objective; objective = NULL; }
	if(col_lb != NULL)      { delete [] col_lb; col_lb = NULL; }
	if(col_ub != NULL)      { delete [] col_ub; col_ub = NULL; }
	if(row_lb != NULL)      { delete [] row_lb; row_lb = NULL; }
	if(row_ub != NULL)      { delete [] row_ub; row_ub = NULL; }

    for (int i = 0; i < rows; i++) {
    	delete added_rows[i];
    }
    delete [] added_rows;

	if(matrix != NULL)      { delete matrix; matrix = NULL; }
}

double OSI_solver::solve(vector<ConstraintVar*>& obj_func, vector<LPConstraint*>& constr, Solution* sol) {

	assert(constr.size() == rows);

	cout << "Solving with OSI" << endl;

	double val;
    try{
        struct tms start, end_build, end_solve, end_all;
        times(&start);

   	cout << "creating objective" << endl;
    create_OSI_objective(obj_func);
   	cout << "creating matrix" << endl;
	create_OSI_matrix(constr);

 //  	dump();
   	cout << "loading problem" << endl;
    //load the problem to OSI
    si->loadProblem(*matrix, col_lb, col_ub, objective, row_lb, row_ub);
   	cout << "done loading problem" << endl;

    //we want to maximize the objective function
    si->setObjSense(-1);

    si->messageHandler()->setLogLevel(0);
    //solve the linear program

    times(&end_build);
   	cout << "solving LP" << endl;
    si->initialSolve();
    times(&end_solve);

   	cout << "getting solution" << endl;
    const double * solution = si->getColSolution();
   	cout << "getting solution value" << endl;
    val = si->getObjValue();

   	cout << "setting solution" << endl;
	if (sol) {
		sol->set_solution(solution,cols);
	}

    times(&end_all);

    //int total_ms = (end_all.tms_utime - start.tms_utime) * 10;
    //int build_ms = (end_build.tms_utime - start.tms_utime) * 10;
    //int solve_ms = (end_solve.tms_utime - end_build.tms_utime) * 10;

    //cout << "Build: " << build_ms << " , Solve: " << solve_ms << " , Total: " << total_ms << "  , Iterations: " << si->getIterationCount() << endl;;


    }
    catch(CoinError & ex){
          cerr << "Exception:" << ex.message() << endl
          << " from method " << ex.methodName() << endl
          << " from class " << ex.className() << endl;
          exit(0);
    };

	return val;
}

void OSI_solver::create_OSI_objective(vector<ConstraintVar*>& obj_func) {

	// Fill the objectives and variable bounds - [0,inf)
	for (int i =0; i < cols; i++) {
		objective[i] = 0.0;
		col_lb[i] = 0.0;
		col_ub[i] = si->getInfinity();
	}

	for (int i =0; i < obj_func.size(); i++) {
		objective[obj_func[i]->var] = obj_func[i]->val;
	}
}

void OSI_solver::create_OSI_matrix(vector<LPConstraint*> &constr) {

	//Define the constraint matrix.
    matrix =  new CoinPackedMatrix(false,0,0);
    matrix->setDimensions(0, cols);

    row_lb = new double[rows];
    row_ub = new double[rows];

    added_rows = new CoinPackedVectorBase*[rows];
    for (int i = 0; i < rows; i++) {
        CoinPackedVector &added_row = *new CoinPackedVector(true);

		vector<ConstraintVar*> cvars = constr[i]->get_vals();
		int index = constr[i]->get_index();
		int nonz = cvars.size();
		for (int j =0; j < nonz;j++) {
            added_row.insert(cvars[j]->var + index, cvars[j]->val);
		}

        added_rows[i] = &added_row;
        row_lb[i] = constr[i]->get_lb();
        row_ub[i] = constr[i]->get_ub();
    }
    matrix->appendRows(rows, added_rows);

}


void OSI_solver::dump() {
	cout << "Problem with inputting data" << endl;
	cout << "Number of rows : " << rows << ", Number of columns : " << cols << endl;

	cout << "Objective : " ;
	for (int i=0; i < cols; i++)
		if (objective[i] != 0)
			cout << " " << objective[i] << "x_" << i;
	cout << endl;
	/*
	cout << "Cols lb : " << col_lb[0];
	for (int i=1;i<cols;i++)
		cout << ", " << col_lb[i];
	cout << endl << "Cols ub : " << col_ub[0];
	for (int i=1;i<cols;i++)
		cout << ", " << col_ub[i];
	cout << endl << "Rows lb : " << row_lb[0];
	for (int i=1;i<rows;i++)
		cout << ", " << row_lb[i];
	cout << endl << "Rows ub : " << row_ub[0];
	for (int i=1;i<rows;i++)
		cout << ", " << row_ub[i];
	cout << endl;
	*/
	matrix->dumpMatrix();
}
#endif
