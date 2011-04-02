#include "feature_extractor.h"

void FeatureExtractor::extract_numeric_features(const void *obj, vector<double>& features) {
    vector<int> f;
    extract_features(obj, f);
    for (int i = 0; i < f.size(); i++) {
        features.push_back(f[i]);
    }
}
