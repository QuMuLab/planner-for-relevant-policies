#ifdef USE_LP

#include "selective_partition_heuristic.h"
#include "probe_state_space_sample.h"
#include "PDB_state_space_sample.h"
#include "../ff_heuristic.h"
#include "../globals.h"
#include "../structural_patterns/state_opt_heuristic.h"
#include "../structural_patterns/SP_globals.h"
#include "../structural_patterns/SP_heuristic.h"
#include "../problem.h"
#include "../search_engine.h"
#include "../blind_search_heuristic.h"
#include <sstream>
#include <fstream>
#include <limits>
#include <stdlib.h>
#include <math.h>

using namespace std;

SelectivePartitionHeuristic::SelectivePartitionHeuristic(
        int num_parts,
        const char *arg_,
        state_space_sample_t mode,
        partition_type_t partition,
        bool use_test_mode,
        bool init_opt,
        bool use_state_var_features_,
        bool use_uniform_sp_features_):
            test_mode(use_test_mode),
            num_partitions(num_parts),
            arg(arg_),
            use_initial_optimal(init_opt),
            test_mode_out("sel_part.csv"),
            sample_mode(mode),
            partition_type(partition),
            use_state_var_features(use_state_var_features_),
            use_uniform_sp_features(use_uniform_sp_features_)
{
    target_f_fired = false;
    target_f_value_multi = 1.5;
    first_report = true;
}

SelectivePartitionHeuristic::~SelectivePartitionHeuristic() {
    if (uniform) delete uniform;
    if (spfe) delete spfe;
}


StateSpaceSample *SelectivePartitionHeuristic::collect_sample() {
	Heuristic *sample_h = new FFHeuristic();
	sample_h->evaluate(*g_initial_state);
	if (sample_h->is_dead_end()) {
		return NULL;
	}
	int initial_h = sample_h->get_heuristic();
	StateSpaceSample *sample;
	if (sample_mode == Probe) {
		sample = new ProbeStateSpaceSample(initial_h * 2, 1000 * num_partitions, 1000 * num_partitions);
		sample->add_heuristic(sample_h);
	}
	else if (sample_mode == PDB) {
		sample = new PDBStateSpaceSample(initial_h * 2, 1000 * num_partitions, 1000 * num_partitions);
		sample->add_heuristic(new BlindSearchHeuristic);
	}
	else {
		cerr << "Unknown sample mode" << endl;
		exit(443);
	}

	cout << "Getting initial sample" << endl;
	int size = sample->collect();
	cout << "Got initial sample of: " << size << endl;

	return sample;
}

void SelectivePartitionHeuristic::build_clusters(StateSpaceSample *sample) {
    if (use_initial_optimal && sample_mode != PartialAStar) {
        medoids.push_back(g_initial_state);
        heuristics.push_back(build_sp_heuristic(arg, new Problem(), g_initial_state));
        medoid_distance.push_back(0);
        heuristic_value.push_back(0);
    }

    if (sample->get_samp().size() == 0) {
        cerr << "****************** Sample is 0 - initial state" << endl;
        medoids.push_back(g_initial_state);
        heuristics.push_back(build_sp_heuristic(arg, new Problem(), g_initial_state));
        medoid_distance.push_back(0);
        heuristic_value.push_back(0);
    }
    else if (sample->get_samp().size() <= num_partitions) {
        cerr << "****************** Sample is too small - using all states in sample" << endl;
        sample_t::const_iterator it;
        for (it = sample->get_samp().begin(); it != sample->get_samp().end(); it++) {
            const State &s = (*it).first;
            const State *s2 = new State(s);
            medoids.push_back(s2);
            heuristics.push_back(build_sp_heuristic(arg, new Problem(), s2));
            medoid_distance.push_back(0);
            heuristic_value.push_back(0);
        }
    }
    else {
    	cout << "Choosing representatives" << endl;
        partition_chooser->choose_reps_and_create_heuristics(sample);
    	cout << "End choosing representatives" << endl;

        for (int i = 0; i < partition_chooser->get_representatives().size(); i++) {
            medoids.push_back(partition_chooser->get_representatives()[i]);
            heuristics.push_back(partition_chooser->get_heuristics()[i]);
            medoid_distance.push_back(0);
            heuristic_value.push_back(0);
        }
    }
}

void SelectivePartitionHeuristic::initialize() {
    int num_clusters = num_partitions;
    if (use_initial_optimal)
        num_clusters = num_partitions - 1;

    switch (partition_type) {
    case random:
        cout << "Using Random Partitioning" << endl;
        partition_chooser = new RandomPartitionChooser(num_clusters, arg);
        break;
    case cluster:
        cout << "Using Clustering for Partitioning" << endl;
        partition_chooser = new ClusteringPartitionChooser(num_clusters,
                use_state_var_features,
                use_uniform_sp_features,
                arg);
        break;
    case greedy:
        cout << "Using Greedy MaxMin Method for Partitioning" << endl;
        partition_chooser = new GreedyMinMaxPartitionChooser(num_clusters, arg);
        break;
    case old_greedy:
        cout << "Using Greedy Method for Partitioning" << endl;
        partition_chooser = new OldBadGreedyPartitionChooser(num_clusters, arg);
        break;
    }


    if (sample_mode == PartialAStar) {
        cout << "Using partial-A* sampling" << endl;
        SPHeuristic *sph;
        if (use_initial_optimal) {
            cout << "Initializing Initial Optimal SP Heuristic" << endl;
            sph = (SPHeuristic *) build_sp_heuristic(arg, new Problem(), g_initial_state);
            medoids.push_back(g_initial_state);
        }
        else {
            cout << "Initializing Uniform SP Heuristic" << endl;
            sph = new SPHeuristic();
            sph->set_strategy(FORKS_ONLY);
            sph->set_cost_partitioning_strategy(UNIFORM);
            sph->set_singletons_strategy(NECESSARY);
            medoids.push_back(NULL);
        }

        heuristics.push_back(sph);
        heuristic_value.push_back(0);
        medoid_distance.push_back(0);
    }
    else {
        cout << "Collecting State Space Sample" << endl;
        StateSpaceSample *sample = collect_sample();
        if (sample != NULL) {
        	cout << "Building clusters" << endl;
            build_clusters(sample);
        	cout << "End building clusters" << endl;
            delete sample;
        }
    }

    for (int i = 0; i < medoids.size(); i++) {
        vector<int> discrete_f;
        vector<double> numeric_f;
        medoid_features.push_back(make_pair(discrete_f, numeric_f));
    }


    if (use_uniform_sp_features) {
        uniform = new SPHeuristic();
        uniform->set_strategy(get_sp_strategy(arg));
        uniform->set_cost_partitioning_strategy(UNIFORM);
        uniform->set_singletons_strategy(NECESSARY);
        spfe = new SPEnsembleValuesFeatureExtractor(uniform);
    }

    for (int i = 0; i < medoids.size(); i++) {
        vector<int> df;
        vector<double> nf;
        medoid_features.push_back(make_pair(df, nf));
        if (medoids[i] != NULL) {
            extract_features(*medoids[i], medoid_features[i]);
        }
    }

}

bool SelectivePartitionHeuristic::reach_state(const State& parent_state, const Operator &op,
	        		const State& state) {
	int ret = false;
	int val;
	for (int i = 0; i < heuristics.size(); i++) {
		if (heuristics[i] != NULL) {
			val = heuristics[i]->reach_state(parent_state, op, state);
			ret = ret || val;
		}
	}
	return ret;
}

void SelectivePartitionHeuristic::print_statistics() const {

}

void SelectivePartitionHeuristic::extract_features(const State &s, pair<vector<int>, vector<double> > &state_features) {
    if (use_uniform_sp_features) {
        spfe->extract_numeric_features(&s, state_features.second);
    }
    if (use_state_var_features) {
        for (int j = 0; j < g_variable_domain.size(); j++) {
            state_features.first.push_back( s[j]);
        }
    }
}


double SelectivePartitionHeuristic::distance_metric(pair<vector<int>, vector<double> > &state_features, int medoid_index) {
	double dist = 0;
	assert(use_state_var_features || use_uniform_sp_features);
	if (use_state_var_features) {
        for (int i = 0; i < g_variable_domain.size(); i++) {
            if (state_features.first[i] != medoid_features[medoid_index].first[i])
                dist++;
        }
	}
	if (use_uniform_sp_features) {
	    vector<double> &features = state_features.second;
	    vector<double> &features_med = medoid_features[medoid_index].second;

	    assert(features.size() == features_med.size());

	    for (int i = 0; i < features.size(); i++) {
	        dist = dist + ((features[i] - features_med[i]) * (features[i] - features_med[i]));
	    }
	}

	return dist;
}

int SelectivePartitionHeuristic::compute_heuristic(const State& state) {
	if (heuristics.size() == 0) {
		return DEAD_END;
	}

	double min_distance = numeric_limits<double>::max();
	int min_index = -1;
	pair<vector<int>, vector<double> > state_features;
	extract_features(state, state_features);
	for (int i = 0; i < heuristics.size(); i++) {
		if (heuristics[i] != NULL && medoids[i] != NULL) {
			double dist = distance_metric(state_features, i);
			if (dist < min_distance) {
				min_distance = dist;
				min_index = i;
			}
			else if (dist == min_distance) {
				if ((rand() % 2) == 0) {
					min_index = i;
				}
			}
		}
	}

	if (test_mode) {
		double min_distance = numeric_limits<int>::max();
		int max_eval = numeric_limits<int>::min();
		int num_minimums = 0;
		for (int i = 0; i < heuristics.size(); i++) {
			if (heuristics[i] != NULL) {
			    double dist = numeric_limits<int>::max();
			    if (medoids[i] != NULL)
			        dist = distance_metric(state_features, i);
				int eval = numeric_limits<int>::max();
				heuristics[i]->evaluate(state);
				if (!heuristics[i]->is_dead_end()) {
					eval = heuristics[i]->get_value();
				}
				else // For max return;
					return DEAD_END;

				medoid_distance[i] = dist;
				heuristic_value[i] = eval;
				if (dist < min_distance) {
					min_distance = dist;
					num_minimums = 1;
				}
				else if (dist == min_distance) {
					num_minimums++;
				}

				if (eval > max_eval) {
					max_eval = eval;
				}
			}
			else {
				medoid_distance[i] = numeric_limits<int>::max();
				heuristic_value[i] = 0;
			}
			test_mode_out << medoid_distance[i] << ",  " << heuristic_value[i] << ",  ";
		}

		double score = 0;
		for (int i = 0; i < heuristics.size(); i++) {
			if ((medoid_distance[i] == min_distance) && (heuristic_value[i] == max_eval)) {
				score += 1;
			}
		}
		score = score / num_minimums;

		test_mode_out << score << endl;
		return max_eval;   // For max return;
	}

	heuristics[min_index]->evaluate(state);
	if (heuristics[min_index]->is_dead_end()) {
		return DEAD_END;
	}
	else {
		return heuristics[min_index]->get_value();
	}
}


void SelectivePartitionHeuristic::report_f_value(const SearchEngine *search, int f) {
    if (sample_mode == PartialAStar) {
        if (first_report) {
            first_report = false;
            target_f_value = ceil(target_f_value_multi * f);
            cout << "****** Target f value: " << target_f_value << endl;
        }
        if (!target_f_fired && f >= target_f_value) {
            target_f_fired = true;
            cout << "****** Target f value reached ******" << endl;

            StateSpaceSample sample;
            vector<int> h;
            h.push_back(0);
            int count = 0;

            __gnu_cxx::hash_map<StateProxy, SearchNodeInfo>::const_iterator it;
            for (it = search->get_search_space().begin(); it != search->get_search_space().end(); it++) {
                pair<StateProxy, SearchNodeInfo> p = *it;
                if (p.second.status == SearchNodeInfo::OPEN || p.second.status == SearchNodeInfo::NEW) {
                    count++;
                }
            }

            int desired_size = 1000 * num_partitions;
            double prob = (double) desired_size / (double) count;

            for (it = search->get_search_space().begin(); it != search->get_search_space().end(); it++) {
                pair<StateProxy, SearchNodeInfo> p = *it;
                if (p.second.status == SearchNodeInfo::OPEN || p.second.status == SearchNodeInfo::NEW) {
                    if (drand48() < prob) {
                        State s(p.first.state_data);
                        h[0] = p.second.h;

                        sample.add_state(s, h);
                    }
                }
            }

            cout << endl << "Found " << count << " states - using " << sample.get_samp().size() << endl;
            build_clusters(&sample);
        }
    }
}
#endif
