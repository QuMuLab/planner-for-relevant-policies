#ifndef SELECTIVE_PARTITION_HEURISTIC_H_
#define SELECTIVE_PARTITION_HEURISTIC_H_

#ifdef USE_LP

#include "../heuristic.h"
#include "../state.h"
#include "state_space_sample.h"
#include "partition_chooser.h"
#include "sp_ensemble_values_feature_extractor.h"

#include <fstream>

class SelectivePartitionHeuristic: public Heuristic {
public:
    enum partition_type_t {random = 0, cluster = 1, greedy = 2, old_greedy = 999};
private:
	bool test_mode;
	int num_partitions;
	vector<const State *> medoids;
	vector<pair<vector<int>, vector<double> > >medoid_features;
	vector<Heuristic *> heuristics;
	vector<int> heuristic_value;
	vector<double> medoid_distance;
	const char *arg;
	SPEnsembleValuesFeatureExtractor *spfe;
	SPHeuristic *uniform;

	int target_f_value;
    double target_f_value_multi;
    bool target_f_fired;
    bool first_report;
    bool use_initial_optimal;

	ofstream test_mode_out;
	state_space_sample_t sample_mode;
	partition_type_t partition_type;

	bool use_state_var_features;
	bool use_uniform_sp_features;

	StateSpaceSample *collect_sample();
	PartitionChooser *partition_chooser;
	void build_clusters(StateSpaceSample *sample);
protected:
	void extract_features(const State &s, pair<vector<int>, vector<double> > &state_features);
	virtual double distance_metric(pair<vector<int>, vector<double> > &state_features, int medoid_index);
	virtual void initialize();
	virtual int compute_heuristic(const State& state);
public:
	SelectivePartitionHeuristic(int num_partitions,
	        const char *arg, state_space_sample_t mode = PDB,
	        partition_type_t partition = cluster,
	        bool use_test_mode = false,
	        bool init_opt = false,
	        bool use_state_var_features = false,
	        bool use_uniform_sp_features = false);
	virtual ~SelectivePartitionHeuristic();

	virtual void print_statistics() const;
	virtual bool reach_state(const State& parent_state, const Operator &op,
						const State& state);

	void set_sample_mode(state_space_sample_t mode) {sample_mode = mode;}
	state_space_sample_t get_sample_mode() const {return sample_mode;}

	virtual void report_f_value(const SearchEngine *search, int f);
};

#endif /* SELECTIVE_PARTITION_HEURISTIC_H_ */
#endif
