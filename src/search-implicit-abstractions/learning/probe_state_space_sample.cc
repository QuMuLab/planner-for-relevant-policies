#include "probe_state_space_sample.h"
#include "../successor_generator.h"
#include "../heuristic.h"
#include <limits>

ProbeStateSpaceSample::ProbeStateSpaceSample(int goal_depth, int probes = 10, int size = 100):
	goal_depth_estimate(goal_depth), max_num_probes(probes), min_training_set_size(size),
	temporary_sample(&samp)
{
	expanded = 0;
	generated = 0;
	add_every_state = true;
}

ProbeStateSpaceSample::~ProbeStateSpaceSample() {
}

int ProbeStateSpaceSample::collect() {
	cout << "Probe state space sample" << endl;
	int num_probes = 0;
	while ((samp.size() < min_training_set_size) && (num_probes < max_num_probes)) {
		num_probes++;
		//cout << "Probe: " << num_probes << " - " << sample.size() << endl;

		send_probe(goal_depth_estimate);
	}

	branching_factor = (double) generated / (double) expanded;

	return samp.size();
}

int ProbeStateSpaceSample::get_aggregate_value(vector<int> &values) {
    int max = numeric_limits<int>::min();
    for (int i = 0; i < values.size(); i++) {
        if (values[i] > max)
            max = values[i];
    }
    return max;
}

void ProbeStateSpaceSample::send_probe(int depth_limit) {
	vector<const Operator *> applicable_ops;
	vector<int> h_s;

	State s = *g_initial_state;
	if (temporary_sample->find(s) == temporary_sample->end()) {
		for (int i = 0; i < heuristics.size(); i++) {
		    heuristics[i]->evaluate(*g_initial_state);
		    (*temporary_sample)[s].push_back(heuristics[i]->get_heuristic());
		}
	}
	for (int dpth = 0; (dpth < depth_limit) && (samp.size() < min_training_set_size); dpth++) {
		expanded++;
		applicable_ops.clear();
		g_successor_generator->generate_applicable_ops(s, applicable_ops);

		if (applicable_ops.size() == 0) {
			break;
		}
		generated = generated + applicable_ops.size();
		h_s.resize(applicable_ops.size());

		for (int op_num = 0; op_num < applicable_ops.size(); op_num++) {
			// generate and add to training set all successors
			const Operator *op = applicable_ops[op_num];
			State succ(s, *op);

			for (int j = 0; j < heuristics.size(); j++) {
			    clock_t before = times(NULL);
			    heuristics[j]->reach_state(s, *op, succ);
			    heuristics[j]->evaluate(succ);
			    clock_t after = times(NULL);
			    computation_time[j] += after - before;
                if (heuristics[j]->is_dead_end()) {
                	(*temporary_sample)[succ].push_back(numeric_limits<int>::max());
                	if (add_every_state) {
                		samp[succ].push_back(numeric_limits<int>::max());
                	}
                }
                else {
                	(*temporary_sample)[succ].push_back(heuristics[j]->get_heuristic());
                	if (add_every_state) {
                		samp[succ].push_back(heuristics[j]->get_heuristic());
                	}
                }
			}

			h_s[op_num] = get_aggregate_value((*temporary_sample)[succ]);
		}

		// choose operator at random
		int op_num = choose_operator(h_s);

		const Operator *op = applicable_ops[op_num];

		State succ(s, *op);

		for (int i = 0; i < heuristics.size(); i++) {
		    heuristics[i]->reach_state(s, *op, succ);
		}
		if (test_goal(succ)) {
		    cout << "Found goal" << endl;
			break;
		}

		s = succ;
	}

	if (!add_every_state) {
		for (int j = 0; j < heuristics.size(); j++) {
			heuristics[j]->evaluate(s);
			if (!heuristics[j]->is_dead_end()) {
				samp[s].push_back(heuristics[j]->get_heuristic());
			}
		}
	}
}
