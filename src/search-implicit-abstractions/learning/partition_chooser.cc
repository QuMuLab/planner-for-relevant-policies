#include "partition_chooser.h"

#include <sstream>
#include <fstream>
#include <limits>
#include <stdlib.h>
#include <math.h>

#include "../structural_patterns/state_opt_heuristic.h"
#include "../structural_patterns/SP_heuristic.h"
#include "../structural_patterns/SP_globals.h"
#include "sp_ensemble_values_feature_extractor.h"

PartitionChooser::PartitionChooser(int num_parts,const char *arg):num_partitions(num_parts), h_arg(arg) {
}

PartitionChooser::~PartitionChooser() {
}

Heuristic *PartitionChooser::create_heuristic(const State &s, Problem* prob) {

	return build_sp_heuristic(h_arg, prob, &s);
//    StateOptimalHeuristic *soh = new StateOptimalHeuristic(s, prob);
//    soh->set_strategy(FORKS_ONLY);
//    soh->set_cost_partitioning_strategy(INITIAL_OPTIMAL);
//    soh->set_singletons_strategy(NECESSARY);
//    return soh;
}

int PartitionChooser::choose_reps_and_create_heuristics(StateSpaceSample *sample) {
    int k = choose(sample);

    cout << "Got " << k << " - " << representatives.size() << endl;
    Problem* prob = new Problem();
    for (int i = 0; i < representatives.size(); i++) {
        const State *state = representatives[i];
        if (!prob->is_goal(state)) {
            Heuristic *h = create_heuristic(*state, prob);
            heuristics.push_back(h);
        }
        else {
            cout << "Got goal state as medoid, skipping" << endl;
            heuristics.push_back(NULL);
        }
    }
    return heuristics.size();
}

/*****************************************************************************/
/*  ClusteringPartitionChooser                                               */
/*****************************************************************************/
ClusteringPartitionChooser::ClusteringPartitionChooser(int num_parts,
        bool use_state_var_features_,
        bool use_uniform_sp_features_,
        const char *arg):
        PartitionChooser(num_parts, arg),
        use_state_var_features(use_state_var_features_),
        use_uniform_sp_features(use_uniform_sp_features_)
{
}

ClusteringPartitionChooser::~ClusteringPartitionChooser() {
}

int ClusteringPartitionChooser::choose(StateSpaceSample *sample) {

    //sample->dump_arff("sample.arff");

    SPHeuristic *uniform = new SPHeuristic();
    uniform->set_strategy(get_sp_strategy(h_arg));
    uniform->set_cost_partitioning_strategy(UNIFORM);
    uniform->set_singletons_strategy(NECESSARY);
    SPEnsembleValuesFeatureExtractor *spfe = new SPEnsembleValuesFeatureExtractor(uniform);
    int cnt = sample->dump_arff("sample.arff", spfe, use_state_var_features, use_uniform_sp_features);
    delete spfe;

    if (cnt == 0) {
        cerr << "******************  Number of non dead-end states is 0 - using initial state" << endl;
        representatives.push_back(g_initial_state);
        return representatives.size();
    }
    else if (cnt <= num_partitions) {
        cerr << "******************  Number of non dead-end states too small - using all non dead-end states in sample" << endl;
        sample_t::const_iterator it;
        for (it = sample->get_samp().begin(); it != sample->get_samp().end(); it++) {
            const State &s = (*it).first;
            uniform->evaluate(s);
            if (!uniform->is_dead_end()) {
                const State *s2 = new State(s);
                representatives.push_back(s2);
            }
        }
        return representatives.size();
    }


    stringstream javastring;
    char exename[256];
    getexename(exename, 256);
    string s_exename = exename;
    string s_dir = s_exename.substr(0, s_exename.find_last_of('/'));
    javastring << "java -classpath " << s_dir << ":" << s_dir << "/weka.jar cluster.Cluster sample.arff ";
    javastring << num_partitions;
    javastring << " centroids";
    cout << javastring.str() << endl;
    cout << "Success: " << system(javastring.str().c_str());

    ifstream centroids_in("centroids");
    vector<State*> centroids;
    int num_centroids;
    check_magic(centroids_in, "begin_centroids");
    centroids_in >> num_centroids;
    cout << "Num centroids: " << num_centroids << endl;
    for(int i = 0; i < num_centroids; i++) {
        int address;
        centroids_in >> address;
        cout << address << endl;
        State *s = (State *) address;
        /*
        s->dump();
        vector<double> feat;
        spfe->extract_numeric_features(s, feat);
        for (int i = 0; i < feat.size(); i++) {
            cout << feat[i] << " ";
        }
        cout << endl;
        */
        State *s2 = new State(*s);
        representatives.push_back(s2);
        cout << "centroid " << i << endl;
        s2->dump();
    }
    check_magic(centroids_in, "end_centroids");
    return representatives.size();
}
/*****************************************************************************/
/*  RandomPartitionChooser                                                   */
/*****************************************************************************/
RandomPartitionChooser::RandomPartitionChooser(int num_parts, const char *arg):
        PartitionChooser(num_parts, arg)
{
}

RandomPartitionChooser::~RandomPartitionChooser() {
}

int RandomPartitionChooser::choose(StateSpaceSample *sample) {
    for (int i = 0; i < num_partitions; i++) {
        cout << "State " << i << endl;
        const State *s = new State(sample->get_random_state());
        s->dump();
        representatives.push_back(s);
    }
    return representatives.size();
}
/*****************************************************************************/
/*  GreedyPartitionChooser                                                   */
/*****************************************************************************/
OldBadGreedyPartitionChooser::OldBadGreedyPartitionChooser(int num_parts, const char *arg):
        PartitionChooser(num_parts, arg)
{
    norm_type = l2;
    agg_type = sum;
    normalize_vectors = false;
}

OldBadGreedyPartitionChooser::~OldBadGreedyPartitionChooser() {
}

void OldBadGreedyPartitionChooser::normalize(vector<double> &v) {
    if (normalize_vectors) {
        double sum = 0;
        for (int i = 0; i < v.size(); i++) {
            sum = sum + v[i];
        }
        for (int i = 0; i < v.size(); i++) {
            v[i] = v[i] / sum;
        }
    }
}

double OldBadGreedyPartitionChooser::distance(vector<double> &v1, vector<double>& v2) {
    assert(v1.size() == v2.size());
    double ret = 0;
    switch (norm_type) {
    case l1:
        for (int i = 0; i < v1.size(); i++) {
            ret = ret + fabs(v1[i] - v2[i]);
        }
        break;
    case l2:
        for (int i = 0; i < v1.size(); i++) {
            ret = ret + ((v1[i] - v2[i])*(v1[i] - v2[i]));
        }
        ret = sqrt(ret);
        break;
    case linf:
        for (int i = 0; i < v1.size(); i++) {
            if (fabs(v1[i] - v2[i]) > ret) {
                ret = fabs(v1[i] - v2[i]);
            }
        }
        break;
    }
    return ret;
}

int OldBadGreedyPartitionChooser::choose_reps_and_create_heuristics(StateSpaceSample *sample) {
    sample_t samp = sample->get_samp();
    //create state optimal heuristic for initial state
    Problem *prob = new Problem();
    representatives.push_back(g_initial_state);
    Heuristic *h0 = create_heuristic(*g_initial_state, prob);
    h0->evaluate(*g_initial_state);
    heuristics.push_back(h0);
    vector<vector<double> > self_features;
    vector<double> v;
    self_features.push_back(v);
#ifdef USE_LP
    ((StateOptimalHeuristic *)heuristics[0])->get_ensemble_values(*g_initial_state, self_features[0]);
#else
		cout << "No LP Solver defined in this version" << endl;
		exit(1);
#endif
    normalize(self_features[0]);


    for (int i = 1; i < num_partitions; i++) {
        double best_agg_distance =  0;
        const State *best_state = NULL;
        int tie_counter = 0;

        // go over all states in sample
        sample_t::const_iterator it;
        for (it = samp.begin(); it != samp.end(); it++) {
            const State *state = &(*it).first;

            if (prob->is_goal(state)) continue;

            // calculate aggregate (min/sum) distance for state
            double agg_distance = 0;
            if (agg_type == min) {
                agg_distance = numeric_limits<double>::max();
            }
            for (int j = 0; j < heuristics.size(); j++) {
                vector<double> features;
#ifdef USE_LP
                StateOptimalHeuristic *hj = (StateOptimalHeuristic *)heuristics[j];
                hj->get_ensemble_values(*state, features);
#else
		cout << "No LP Solver defined in this version" << endl;
		exit(1);
#endif
                normalize(features);
                double d = distance(self_features[j], features);
                if (agg_type == sum) {
                    agg_distance = agg_distance + d;
                }
                else {
                    if (d < agg_distance) {
                        agg_distance = d;
                    }
                }
            }
            // update best state
            if (agg_distance > best_agg_distance) {
                best_agg_distance = agg_distance;
                best_state = state;
                tie_counter = 1;
            }
            else if (agg_distance == best_agg_distance) {
                tie_counter++;
                if ((rand() % tie_counter) == 0) {
                    best_agg_distance = agg_distance;
                    best_state = state;
                }
            }
        }
        // create new representative
        // create new state so we can free sample memory later
        cout << "Best distance: " << best_agg_distance << endl;

        State *new_rep = new State(*best_state);
        Heuristic *new_h = create_heuristic(*new_rep, prob);
        new_h->evaluate(*new_rep);
        representatives.push_back(new_rep);
        heuristics.push_back(new_h);
        vector<double> new_v;
#ifdef USE_LP
        ((StateOptimalHeuristic *)new_h)->get_ensemble_values(*new_rep, new_v);
#else
		cout << "No LP Solver defined in this version" << endl;
		exit(1);
#endif
        normalize(new_v);
        self_features.push_back(new_v);

    }

    return heuristics.size();
}

/*****************************************************************************/
/*  GreedyPartitionChooser                                                   */
/*****************************************************************************/
GreedyMinMaxPartitionChooser::GreedyMinMaxPartitionChooser(int num_parts, const char *arg):
        PartitionChooser(num_parts, arg)
{
}

GreedyMinMaxPartitionChooser::~GreedyMinMaxPartitionChooser() {
}

int GreedyMinMaxPartitionChooser::choose_reps_and_create_heuristics(StateSpaceSample *sample) {
    sample_t samp = sample->get_samp();
    Problem *prob = new Problem();

    SPHeuristic *sph = new SPHeuristic();
    sph->set_strategy(FORKS_ONLY);
    sph->set_cost_partitioning_strategy(UNIFORM);
    sph->set_singletons_strategy(NECESSARY);
    heuristics.push_back(sph);

    for (int i = 0; i < num_partitions; i++) {
        const State *best_state = NULL;
        int tie_counter = 0;
        int min_max = numeric_limits<int>::max();

        // go over all states in sample
        sample_t::const_iterator it;
        for (it = samp.begin(); it != samp.end(); it++) {
            const State *state = &(*it).first;

            if (prob->is_goal(state)) continue;

            int max = 0;
            for (int j = 0; j < heuristics.size(); j++) {
                heuristics[j]->evaluate(*state);
                if (heuristics[j]->is_dead_end()) {
                    max = numeric_limits<int>::max();
                    break;
                }
                else {
                    if (heuristics[j]->get_value() > max)
                        max = heuristics[j]->get_value();
                }
            }

            if (max < min_max) {
                min_max = max;
                best_state = state;
                tie_counter = 1;
            }
            else if (max == min_max) {
                tie_counter++;
                if ((rand() % tie_counter) == 0) {
                    best_state = state;
                }
            }
        }
        // create new representative
        // create new state so we can free sample memory later
        cout << "MinMax: " << min_max << endl;

        State *new_rep = new State(*best_state);
        Heuristic *new_h = create_heuristic(*new_rep, prob);
        new_h->evaluate(*new_rep);
        representatives.push_back(new_rep);
        heuristics.push_back(new_h);
    }

    heuristics.erase(heuristics.begin());

    return heuristics.size();
}

