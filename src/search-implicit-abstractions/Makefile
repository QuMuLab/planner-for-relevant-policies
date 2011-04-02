HEADERS = abstraction.h operator_registry.h variable_order_finder.h \
          heuristic.h \
	  lm_cut_heuristic.h \
          cyclic_cg_heuristic.h cg_heuristic.h \
          additive_heuristic.h \
          fd_heuristic.h ff_heuristic.h relaxation_heuristic.h\
	  max_heuristic.h \
          goal_count_heuristic.h blind_search_heuristic.h \
          globals.h \
	  domain_transition_graph.h \
          operator.h state.h successor_generator.h causal_graph.h \
	  eager_greedy_best_first_search.h axioms.h cache.h \
          search_engine.h closed_list.h \
          timer.h open_lists/standard_scalar_open_list.h \
          open_lists/tiebreaking_open_list.h open_lists/alternation_open_list.h \
		  open_lists/pareto_open_list.h \
	  search_node_info.h search_space.h fh_open_list.h a_star_search.h general_eager_best_first_search.h \
	  landmarks/landmarks_graph.h landmarks/landmarks_graph_rpg_sasp.h \
	  landmarks/landmarks_count_heuristic.h landmarks/exploration.h \
	  landmarks/landmark_status_manager.h \
	  landmarks/landmarks_graph_rpg_exhaust.h landmarks/landmarks_graph_zhu_givan.h \
	  landmarks/util.h landmarks/lama_ff_synergy.h landmarks/landmark_cost_assignment.h\
	  landmarks/landmarks_graph_rpg_search.h\
	  hm_heuristic.h \
	  weighted_evaluator.h sum_evaluator.h g_evaluator.h general_lazy_best_first_search.h\
	  lazy_best_first_search_engine.h lazy_wa_star.h \
	  learning/feature_extractor.h \
	  learning/state_vars_feature_extractor.h \
	  learning/composite_feature_extractor.h \
	  learning/node_info_feature_extractor.h \
	  learning/landmarks_feature_extractor.h \
	  learning/g_feature_extractor.h \
	  learning/state_space_sample.h \
	  learning/PDB_state_space_sample.h \
	  learning/probe_state_space_sample.h \
	  learning/classifier.h \
	  learning/naive_bayes_classifier.h \
	  learning/AODE.h \
	  learning/selective_max_heuristic.h \
          learning/maximum_heuristic.h \
	  enforced_hill_climbing_search.h pref_evaluator.h search_progress.h\
          structural_patterns/binary_forks.h \
          structural_patterns/binary_forks_on.h \
          structural_patterns/binary_forks_gen.h \
          structural_patterns/bounded_iforks.h \
          structural_patterns/bounded_iforks_on.h \
          structural_patterns/bounded_iforks_gen.h \
          structural_patterns/composition_mapping.h \
          structural_patterns/domain_abstraction.h \
          structural_patterns/dom_abs_mapping.h \
          structural_patterns/forks_abstraction.h \
          structural_patterns/general_abstraction.h \
          structural_patterns/ifork_root_path.h \
          structural_patterns/iforks_abstraction.h \
          structural_patterns/MOSEK_solver.h \
          structural_patterns/OSI_solver.h \
          structural_patterns/mapping.h \
          structural_patterns/online_heuristic.h \
          structural_patterns/init_opt_heuristic.h \
          structural_patterns/op_hash_dom_abs_mapping.h \
          structural_patterns/op_hash_mapping.h \
          structural_patterns/op_hash_var_proj_mapping.h \
          structural_patterns/projection_gen.h \
          structural_patterns/projection_on.h \
          structural_patterns/var_projection.h \
          structural_patterns/var_proj_mapping.h \
          structural_patterns/LP_binary_forks.h \
          structural_patterns/LP_binary_forks_bounds.h \
          structural_patterns/LP_bounded_ifork_gen.h \
          structural_patterns/LP_bounded_iforks_off.h \
          structural_patterns/LP_projection_off.h \
          structural_patterns/LP_projection_gen.h \
          structural_patterns/LP_solver.h \
          structural_patterns/LP_heuristic.h \
          structural_patterns/LPConstraint.h \
          structural_patterns/LP_binary_fork_gen.h \
          structural_patterns/solution_method.h \
          structural_patterns/solution.h \
          structural_patterns/SP_heuristic.h \
          structural_patterns/SP_globals.h \
          lm_graph_paths.h \
          lm_enriched_heuristic.h \
          lm_enriched_no_actions_heuristic.h \
          lm_enriched_paths_heuristic.h \
          landmark_enriched_heuristic.h \
          structural_patterns/state_opt_heuristic.h \
          learning/selective_partition_heuristic.h \
        problem.h learning/partition_chooser.h \
        learning/sp_ensemble_values_feature_extractor.h

ifeq ($(USE_LP_MOSEK),1)
ifndef MOSEKLM_LICENSE_FILE
echo Please define the shell variable MOSEKLM_LICENSE_FILE
endif
MOSEK_BASE = $(MOSEKLM_LICENSE_FILE)/..
#MOSEKCCOPT = -DUSE_MOSEK -DUSE_LP -I$(MOSEK_BASE)/tools/platform/linux32x86/h
#MOSEKLINKOPT = -L$(MOSEK_BASE)/tools/platform/linux32x86/bin -pthread -lmosek -lc -ldl -lm
MOSEKCCOPT = -DUSE_MOSEK -DUSE_LP -I$(MOSEK_BASE)/tools/platform/linux64x86/h
MOSEKLINKOPT = -L$(MOSEK_BASE)/tools/platform/linux64x86/bin -pthread -lmosek64 -lc -ldl -lm
#MOSEKCCOPT = -DUSE_MOSEK -I/storage13/mosek/6/tools/platform/linux32x86/h
#MOSEKLINKOPT = -L/storage13/mosek/6/tools/platform/linux32x86/bin -pthread -lmosek -lc -ldl -lm
RELEASELINKOPT = $(MOSEKLINKOPT)
endif

ifeq ($(STATE_VAR_SHORT),1)
DLFAG+=-DSTATE_VAR_SHORT
endif

ifeq ($(HIGH_COST_ACTIONS),1)
DLFAG+=-DHIGH_COST_ACTIONS
endif

SOURCES = planner.cc $(HEADERS:%.h=%.cc)
OBJECTS = $(SOURCES:%.cc=obj/%.o)
PROFILE_OBJECTS = $(SOURCES:%.cc=obj/%.profile.o)
RELEASE_OBJECTS = $(SOURCES:%.cc=obj/%.release.o)

CC = g++
DEPEND = g++ -MM $(MOSEKCCOPT)
#CCOPT         = -m32 -Wall -W -Wno-sign-compare -Wno-deprecated -ansi -pedantic -Werror $(MOSEKCCOPT)
CCOPT         = -m32 -Wall -W -Wno-sign-compare -Wno-deprecated -ansi -Werror $(DLFAG) $(MOSEKCCOPT)
LINKOPT = -m32 $(MOSEKLINKOPT)
RELEASEOPT = $(CCOPT)
RELEASEOPT += -O5 -DNDEBUG -fomit-frame-pointer

## We link statically to allow local compiles to work on the BFG cluster.
## NOTE: This precludes using exceptions; see man gcc on -static-libgcc.
#RELEASEOPT += -static -static-libgcc

## debug, don't optimize
CCOPT += -g
LINKOPT += -g

## debug, optimize
# CCOPT += -O3 -g
# LINKOPT += -g

## no debug, optimize a lot
# CCOPT += -O3 -DNDEBUG

PROFOPT = -pg -O3
# PROFLINKOPT = -lc_p
PROFARGS = oa200000 < profile-input.pre


ifeq ($(USE_LP_CLP),1) 

COIN_ROOT=$(HOME)/software/Osi
COIN_INC_DIR=$(COIN_ROOT)/include/coin
COIN_LIB_DIR=$(COIN_ROOT)/lib
SOLVER=CLP

ifeq ($(SOLVER),CLP)
SOLVER_INC_DIR=$(COIN_INC_DIR)
SOLVER_LIB_DIR=$(COIN_LIB_DIR)
SOLVER_LIBS=$(COIN_LIB_DIR)/libOsiClp.so $(SOLVER_LIB_DIR)/libClp.so
endif

ifeq ($(SOLVER),OSL)
SOLVER_INC_DIR=$(OSL_INC_DIR)
SOLVER_LIB_DIR=$(OSL_LIB_DIR)
SOLVER_LIBS=$(COIN_LIB_DIR)/libOsiOsl.so $(SOLVER_LIB_DIR)/libosl.so
endif

ifeq ($(SOLVER),CPX)
SOLVER_INC_DIR=$(CPX_INC_DIR)
SOLVER_LIB_DIR=$(CPX_LIB_DIR)
SOLVER_LIBS=$(COIN_LIB_DIR)/libOsiCpx.so $(SOLVER_LIB_DIR)/libcplex.a /usr/lib/libpthread.so
endif

COIN_FLAGS = -I$(COIN_INC_DIR) -I$(SOLVER_INC_DIR) -DCOIN_USE_$(SOLVER) -DUSE_OSI 
COIN_LINK_FLAGS = $(COIN_LIB_DIR)/libOsi.so $(COIN_LIB_DIR)/libCoinUtils.so $(SOLVER_LIBS)

CCOPT += $(COIN_FLAGS)
LINKOPT += $(COIN_LINK_FLAGS)
RELEASELINKOPT = $(COIN_LINK_FLAGS)
endif


all: search

#cluster: cluster/Cluster.class 

cluster/Cluster.class: cluster/Cluster.java
	javac -classpath weka.jar weka/clusterers/*.java    
	javac -classpath .:cluster:weka.jar cluster/Cluster.java	

search: $(OBJECTS) cluster
	$(CC) $(LINKOPT) $(OBJECTS)  -o search

profile-search: $(PROFILE_OBJECTS)
	$(CC) $(LINKOPT) $(PROFLINKOPT) $(PROFOPT) $(PROFILE_OBJECTS) \
          -o profile-search

release: release-search 

release-search: $(RELEASE_OBJECTS) cluster 
	$(CC) $(RELEASEOPT) $(RELEASELINKOPT) $(RELEASE_OBJECTS) \
	  -o release-search

PROFILE: profile-search
	./profile-search $(PROFARGS)
	gprof profile-search | cleanup-profile > PROFILE

$(OBJECTS): obj/%.o: %.cc
	mkdir -p $$(dirname $@)
	$(CC) $(CCOPT) -c $< -o $@

$(PROFILE_OBJECTS): obj/%.profile.o: %.cc
	mkdir -p $$(dirname $@)
	$(CC) $(CCOPT) $(PROFOPT) -c $< -o $@

$(RELEASE_OBJECTS): obj/%.release.o: %.cc
	mkdir -p $$(dirname $@)
	$(CC) $(RELEASEOPT) -c $< -o $@

clean:
	rm -rf obj
	rm -f *~ *.pyc
	rm -f Makefile.depend profile-search gmon.out PROFILE core
	rm -f sas_plan
	rm -f cluster/Cluster.class
	rm -f weka/clusterers/*.class

distclean: clean
	rm -f search release-search

## Note: If we just call gcc -MM on a source file that lives within a
## subdirectory, it will strip the directory part in the output. Hence
## the for loop with the sed call.

Makefile.depend: $(SOURCES) $(HEADERS)
	rm -f Makefile.temp
	for source in $(SOURCES) ; do \
	    $(DEPEND) $$source > Makefile.temp0; \
	    objfile=$${source%%.cc}.o; \
	    sed -i -e "s@^[^:]*:@$$objfile:@" Makefile.temp0; \
	    cat Makefile.temp0 >> Makefile.temp; \
	done
	rm -f Makefile.temp0
	sed -e "s@\(.*\)\.o:\(.*\)@obj/\1.o:\2@" Makefile.temp > Makefile.depend
	sed -e "s@\(.*\)\.o:\(.*\)@obj/\1.release.o:\2@" Makefile.temp >> Makefile.depend
	sed -e "s@\(.*\)\.o:\(.*\)@obj/\1.profile.o:\2@" Makefile.temp >> Makefile.depend
	rm -f Makefile.temp

ifneq ($(MAKECMDGOALS),clean)
ifneq ($(MAKECMDGOALS),distclean)
-include Makefile.depend
endif
endif

.PHONY: release clean distclean
