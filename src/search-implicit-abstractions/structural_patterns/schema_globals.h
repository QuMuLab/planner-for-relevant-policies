#ifndef SCHEMA_GLOBALS_H
#define SCHEMA_GLOBALS_H

#include <limits>
#include <cstdlib>
#include <cassert>
#include <string>
#include <vector>
using namespace std;

class ConceptTerm {
	string name;
	vector<string> terms;
	vector<pair<int, double> > subschemas;
public:
	ConceptTerm() {};
	virtual ~ConceptTerm() {};

	pair<int, double> get_min_subschema() {
		double min = std::numeric_limits<int>::max();
		int min_i = -1;
		for(int i=0; i < subschemas.size(); i++)
			if (subschemas[i].second < min) {
				min = subschemas[i].second;
				min_i = i;
			}
		assert(min_i >= 0);
		return subschemas[min_i];
	}

	string get_name() const {return name;}
	void set_name(string cname) {name = cname;}
	void add_term(string tname) {terms.push_back(tname);}
	void add_score(int subschema, double score) {subschemas.push_back(make_pair(subschema, score));}

    const vector<string> &get_term_names() const {return terms;}
};

void read_subschema(istream &in, vector<int>& terms);
ConceptTerm read_conceptTerm(istream &in);

void dump_schema_cover_problem_SAS(const char* filename);

#endif
