#ifndef PARTITIONCHOOSER_H_
#define PARTITIONCHOOSER_H_

#include "state_space_sample.h"
#include "../problem.h"

class PartitionChooser {
protected:
    int num_partitions;
    vector<Heuristic *> heuristics;
    vector<const State *> representatives;
    const char *h_arg;
    virtual int choose(StateSpaceSample *) {return 0;}
    Heuristic *create_heuristic(const State &s, Problem* prob);
public:
    PartitionChooser(int num_partitions, const char *arg);
    virtual ~PartitionChooser();

    virtual int choose_reps_and_create_heuristics(StateSpaceSample *sample);

    const vector<Heuristic *>& get_heuristics() const {return heuristics;}
    const vector<const State *> get_representatives() const {return representatives;}
};

class ClusteringPartitionChooser :public PartitionChooser{
    bool use_state_var_features;
    bool use_uniform_sp_features;
public:
    ClusteringPartitionChooser(int num_partitions,
            bool use_state_var_features,
            bool use_uniform_sp_features,
            const char *arg);
    virtual ~ClusteringPartitionChooser();
    virtual int choose(StateSpaceSample *sample);
};

class RandomPartitionChooser :public PartitionChooser{
public:
    RandomPartitionChooser(int num_partitions, const char *arg);
    virtual ~RandomPartitionChooser();
    virtual int choose(StateSpaceSample *sample);
};

class OldBadGreedyPartitionChooser :public PartitionChooser{
public:
    enum norm_type_t {l1, l2, linf};
    enum distance_agg_t {sum, min};
    OldBadGreedyPartitionChooser(int num_partitions, const char *arg);
    virtual ~OldBadGreedyPartitionChooser();
    virtual int choose_reps_and_create_heuristics(StateSpaceSample *sample);
private:
    norm_type_t norm_type;
    distance_agg_t agg_type;
    bool normalize_vectors;
    double distance(vector<double> &v1, vector<double>& v2);
    void normalize(vector<double> &v);
};

class GreedyMinMaxPartitionChooser :public PartitionChooser{
public:
    GreedyMinMaxPartitionChooser(int num_partitions, const char *arg);
    virtual ~GreedyMinMaxPartitionChooser();
    virtual int choose_reps_and_create_heuristics(StateSpaceSample *sample);
};


#endif /* PARTITIONCHOOSER_H_ */
