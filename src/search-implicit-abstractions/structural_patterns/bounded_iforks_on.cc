#include "SP_globals.h"
#include "bounded_iforks_on.h"
#include "mapping.h"
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
//#include "LP_heuristic.h"

BoundedIforks_ON::BoundedIforks_ON() :BoundedIfork() {
}

BoundedIforks_ON::BoundedIforks_ON(GeneralAbstraction* abs) :BoundedIfork(abs) {
}

BoundedIforks_ON::BoundedIforks_ON(IforksAbstraction* ifork, Domain* abs_domain) :BoundedIfork(ifork, abs_domain) {
}

BoundedIforks_ON::~BoundedIforks_ON() {
//	delete root_paths;
}
