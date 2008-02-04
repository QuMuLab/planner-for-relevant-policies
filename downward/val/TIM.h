#ifndef __TIM
#define __TIM

#include "TimSupport.h"


namespace VAL {
extern TypeChecker * theTC;
};

namespace TIM {
extern TIMAnalyser * TA;

void performTIMAnalysis(char * argv[]);

};

#endif
