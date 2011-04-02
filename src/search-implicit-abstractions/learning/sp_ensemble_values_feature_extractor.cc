#include "sp_ensemble_values_feature_extractor.h"

SPEnsembleValuesFeatureExtractor::SPEnsembleValuesFeatureExtractor(SPHeuristic *sph):
    sp_heuristic(sph) {
    vector<double> features;
    sp_heuristic->evaluate(*g_initial_state);
    sp_heuristic->get_ensemble_values(*g_initial_state, features);
    num_features = features.size();

    normalize = true;
}

SPEnsembleValuesFeatureExtractor::~SPEnsembleValuesFeatureExtractor() {
}

int SPEnsembleValuesFeatureExtractor::get_num_features() {
    return num_features;
}

int SPEnsembleValuesFeatureExtractor::get_feature_domain_size(int) {
    return 0;
}

void SPEnsembleValuesFeatureExtractor::extract_features(const void *, vector<int>& ) {

}

void SPEnsembleValuesFeatureExtractor::extract_numeric_features(const void *obj, vector<double>& features) {
    const State &state = *((const State*) obj);
    sp_heuristic->get_ensemble_values(state, features);
    if (normalize) {
        double sum=0;
        for (int i = 0; i < features.size(); i++) {
            sum += features[i];
        }
        if (sum > 0) {
            for (int i = 0; i < features.size(); i++) {
                features[i] = features[i] / sum;
            }
        }
    }
}
