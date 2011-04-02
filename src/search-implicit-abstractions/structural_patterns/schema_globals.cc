#include "schema_globals.h"

#include "../globals.h"
#include "SP_globals.h"

#include <cstdlib>
#include <iostream>
#include <string>
#include <vector>
#include <fstream>


#include "../state.h"
#include <limits>
#include <unistd.h>
using namespace std;

void read_subschema(istream &in, vector<int>& terms) {
	check_magic(in, "begin_subschema");
	int count;
	in >> count;
	for(int i = 0; i < count; i++) {
		int term;
		in >> term;
		terms.push_back(term);
	}
	check_magic(in, "end_subschema");
}



ConceptTerm read_conceptTerm(istream &in) {
	check_magic(in, "begin_conceptTerm");
	ConceptTerm term;
	string name;
	in >> name;
	term.set_name(name);
	int count;       // The number of terms
	in >> count;
	for(int i = 0; i < count; i++) {
		string term_name;
		in >> term_name;
		term.add_term(term_name);
	}
	in >> count;   // The number of subschemas
	for(int i = 0; i < count; i++) {
		int subschema;
		in >> subschema;
		double score;
		in >> score;
		term.add_score(subschema,score);
	}
	check_magic(in, "end_conceptTerm");
	return term;
}


void dump_schema_cover_problem_SAS(const char* filename) {

	vector<int> variable_domain;

	//const char* input_filename = "output";
	ifstream in("schema");
    ofstream os(filename);

	os << "begin_metric" << endl;
	os << 1 << endl;
	os << "end_metric" << endl;

	os << "begin_variables" << endl;
	// Reading the terms of the schema

	check_magic(in, "begin_terms");
	int count;
	in >> count;
	os << count*2 + 1 << endl;
	os << "Sink 2 -1" << endl;
	variable_domain.push_back(2);
	for(int i = 0; i < count; i++) {
		string name;
	    in >> name;
	    int range;
	    in >> range;
	    range++;
	    variable_domain.push_back(range);
		os << name << " " << range << " -1" << endl;
		os << "Goal:" << name << " 2 -1" << endl;
	    if(range > numeric_limits<state_var_t>::max()) {
	    	cout << "You bet!" << endl;
	    	exit(1);
	    }
	}
	check_magic(in, "end_terms");
	os << "end_variables" << endl;

	os << "begin_state" << endl;
	os << "0" << endl;	 // Sink variable
	for(int i = 0; i < count; i++) {
		os << "0" << endl << "0" << endl;
	}
	os << "end_state" << endl;

	os << "begin_goal" << endl;
	os << count + 1 << endl;
	os << "0 0" << endl;	// Sink variable
	for(int i = 0; i < count; i++) {
		os << 2*i + 2 << " 1" << endl;
	}
	os << "end_goal" << endl;

	// Reading the subschemas of the given schema, keeping in vector places 1 to size.
	// Each entry is a vector of terms.
	int count_subschemas;
	in >> count_subschemas;
	vector<vector<int> > subschemas;
	subschemas.reserve(count_subschemas + 1);
	for(int i = 1; i <= count_subschemas; i++) {
		read_subschema(in, subschemas[i]);
	}
	// Reading the concepts
	int count_concepts;
	in >> count_concepts;
	vector<ConceptTerm> terms;
	for(int i = 0; i < count_concepts; i++) {
		terms.push_back(read_conceptTerm(in));
	}

	// Printing an operator for each concept
	os << count_concepts << endl;
	for(int i = 0; i < count_concepts; i++) {
		os << "begin_operator" << endl;
	   	os << terms[i].get_name() << endl;
	   	os << 0 << endl;
	   	pair<int, double> subschema = terms[i].get_min_subschema();
	   	vector<int>& max_subschema = subschemas[subschema.first];
	   	// Printing a prepost for each term of the max subschema and each value
	   	// then adding an effect moving the goal variable to goal value.
	   	// The variables are 2k-1 and 2k.

	   	int pre_post_size = 0;
    	for(int j = 0; j < max_subschema.size(); j++){
    		int dom = variable_domain[max_subschema[j]];
    		pre_post_size += (dom +1);
    	}
	   	os << pre_post_size << endl;
    	for(int j = 0; j < max_subschema.size(); j++){
    		int var = max_subschema[j];
    		int dom = variable_domain[var];
        	for(int val = 0; val < dom - 1; val++){
        		// Printing conditional effect
        		os << "1 " << var*2 -1 << " " << val << " ";
        		os << var*2 -1 << " -1 " << val+1 << endl;
        	}
        	// If bound reached
    		os << "1 " << var*2 -1 << " " << dom -1 << " ";
    		os << "0 -1 1" << endl;
    		// an effect for covering the variable
    		os << "0 " << var*2 << " -1 1" << endl;
    	}

   		os << subschema.second << endl;
		os << "end_operator" << endl;
	}
	os << "0" << endl;
}
