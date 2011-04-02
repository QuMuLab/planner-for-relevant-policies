
#ifndef SP_ENSEMBLE_VALUES_FEATURE_EXTRACTOR_H_
#define SP_ENSEMBLE_VALUES_FEATURE_EXTRACTOR_H_

#include "feature_extractor.h"
#include "../structural_patterns/SP_heuristic.h"

class SPEnsembleValuesFeatureExtractor: public FeatureExtractor {
private:
    SPHeuristic *sp_heuristic;
    int num_features;

    bool normalize;
public:
    SPEnsembleValuesFeatureExtractor(SPHeuristic *sph);
    virtual ~SPEnsembleValuesFeatureExtractor();

    virtual int get_num_features();
    virtual int get_feature_domain_size(int feature);
    virtual void extract_features(const void *obj, vector<int>& features);
    virtual void extract_numeric_features(const void *obj, vector<double>& features);
};

#endif /* SP_ENSEMBLE_VALUES_FEATURE_EXTRACTOR_H_ */
