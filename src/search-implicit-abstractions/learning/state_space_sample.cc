#include "state_space_sample.h"
#include "../structural_patterns/SP_globals.h"
#include <fstream>

StateSpaceSample::StateSpaceSample() {
	uniform_sampling = false;
}

StateSpaceSample::~StateSpaceSample() {
}

int StateSpaceSample::choose_operator(vector<int> &h_s) {
	int ret = 0;
	if (uniform_sampling) {
		ret = rand() % h_s.size();
	}
	else {
		double sum_inv = 0;
		for (int i = 0; i < h_s.size(); i++) {
			sum_inv = sum_inv + (1.0 / (double) h_s[i]);
		}
		double val = drand48() * sum_inv;
		ret = -1;
		while (val >= 0) {
			ret++;
			val = val - (1.0 / (double) h_s[ret]);
		}
	}
	return ret;
}

int StateSpaceSample::dump_arff(const char* filename) {
    int count = 0;
	sample_t &sample = get_samp();

	ofstream arff_out(filename);

	arff_out << "@RELATION sample_dump" << endl;
	arff_out << endl;

	arff_out << "@ATTRIBUTE name STRING" << endl;
	for (int i = 0; i < g_variable_domain.size(); i++) {
		arff_out << "@ATTRIBUTE " << g_variable_name[i] << " {";
		arff_out << "0";
		for (int j = 1; j < g_variable_domain[i]; j++) {
			arff_out << "," << j ;
		}
		arff_out << "}" << endl;
	}
	arff_out << endl;
	arff_out << "@DATA" << endl;


	sample_t::const_iterator it;
	for (it = sample.begin(); it != sample.end(); it++) {
		const State state = (*it).first;
		arff_out << (long) &(*it).first;
		for (int i = 0; i < g_variable_domain.size(); i++) {
			arff_out << "," << state[i];
		}
		arff_out << endl;
		count++;
	}
	return count;
}

int StateSpaceSample::dump_arff(const char* filename, FeatureExtractor *fe,
        bool use_state_var_features, bool use_uniform_sp_features) {
    int count = 0;
    sample_t &sample = get_samp();

    ofstream arff_out(filename);

    arff_out << "@RELATION sample_dump" << endl;
    arff_out << endl;

    arff_out << "@ATTRIBUTE name STRING" << endl;

    if (use_uniform_sp_features) {
        for (int i = 0; i < fe->get_num_features(); i++) {
            arff_out << "@ATTRIBUTE f" << i << " NUMERIC" << endl;
        }
    }
    if (use_state_var_features) {
        for (int i = 0; i < g_variable_domain.size(); i++) {
            arff_out << "@ATTRIBUTE " << g_variable_name[i] << " {";
            arff_out << "0";
            for (int j = 1; j < g_variable_domain[i]; j++) {
                arff_out << "," << j ;
            }
            arff_out << "}" << endl;
        }
    }

    arff_out << endl;
    arff_out << "@DATA" << endl;


    sample_t::const_iterator it;
    for (it = sample.begin(); it != sample.end(); it++) {
        const State state = (*it).first;
        vector<double> features;
        fe->extract_numeric_features(&state, features);

        bool has_infinity = false;
        for (int i = 0; i < features.size(); i++) {
            if (features[i] >= LP_INFINITY) {
                has_infinity = true;
                break;
            }
        }
        if (has_infinity)
            continue;

        arff_out << (long) &(*it).first;
        if (use_uniform_sp_features) {
            for (int i = 0; i < features.size(); i++) {
                arff_out << ", " << features[i];
            }
        }
        if (use_state_var_features) {
            for (int i = 0; i < g_variable_domain.size(); i++) {
                arff_out << "," << state[i];
            }
        }
        arff_out << endl;
        count++;
    }
    return count;
}


const State StateSpaceSample::get_random_state() {
    sample_t::const_iterator it;
    it = samp.begin();
    int pos = rand() % samp.size();
    //cout << "pos = " << pos << " / " << samp.size() << endl;
    for (int i = 0; i < pos; i++) {
        //cout << i << endl;
        it++;
    }
    return (*it).first;
}

void StateSpaceSample::add_state(const State &state, vector<int>& h_values) {
    samp[state] = h_values;
}
