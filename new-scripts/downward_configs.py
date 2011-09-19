"""
Example configurations taken from
http://alfons.informatik.uni-freiburg.de/downward/PlannerUsage
"""
import sys
import os
import logging
from collections import defaultdict

import tools


HELP = """\
Comma separated list of configurations. They can be specified in the following \
ways: ou, astar_searches, myconfigfile:yY, myconfigfile:lama_configs.
The python modules have to live in the scripts dir.
"""

# Eager A* search with landmark-cut heuristic (previously configuration ou)
ou = '--search "astar(lmcut())"'

fF = """\
--heuristic "hff=ff()" \
--search "lazy_greedy(hff, preferred=hff)"\
"""

yY = """\
--heuristic "hcea=cea()" \
--search "lazy_greedy(hcea, preferred=hcea)"\
"""

yY_eager = """\
--heuristic "hcea=cea()" \
--search "eager_greedy(hcea, preferred=hcea)"\
"""

fFyY = """\
--heuristic "hff=ff()" --heuristic "hcea=cea()" \
--search "lazy_greedy([hff, hcea], preferred=[hff, hcea])"\
"""

lama = """\
--heuristic "hlm,hff=lm_ff_syn(lm_rhw(reasonable_orders=true,lm_cost_type=2,cost_type=2))" \
--search "iterated([lazy_greedy([hff,hlm],preferred=[hff,hlm]),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=5),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=3),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=2),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=1)],\
repeat_last=true)"\
"""

lama_noreas = """\
--heuristic "hlm,hff=lm_ff_syn(lm_rhw(reasonable_orders=false,lm_cost_type=2,cost_type=2))" \
--search "iterated([lazy_greedy([hff,hlm],preferred=[hff,hlm]),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=5),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=3),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=2),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=1)],\
repeat_last=true)"\
"""

lama_unit = """\
--heuristic "hlm,hff=lm_ff_syn(lm_rhw(reasonable_orders=true,lm_cost_type=1,cost_type=1))" \
--search "iterated([lazy_greedy(hff,hlm,preferred=(hff,hlm),cost_type=1),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=5,cost_type=1),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=3,cost_type=1),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=2,cost_type=1),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=1,cost_type=1)],\
repeat_last=true)"\
"""

lama_noreas_unit = """\
--heuristic "hlm,hff=lm_ff_syn(lm_rhw(reasonable_orders=false,lm_cost_type=1,cost_type=1))" \
--search "iterated([lazy_greedy([hff,hlm],preferred=[hff,hlm],cost_type=1),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=5,cost_type=1),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=3,cost_type=1),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=2,cost_type=1),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=1,cost_type=1)],\
repeat_last=true)"\
"""

lama_newhybrid = """\
--heuristic "hlm1,hff1=lm_ff_syn(lm_rhw(reasonable_orders=false,lm_cost_type=1,cost_type=1))" \
--heuristic "hlm2,hff2=lm_ff_syn(lm_rhw(reasonable_orders=false,lm_cost_type=2,cost_type=2))" \
--search "iterated([lazy_greedy([hff1,hlm1],preferred=[hff1,hlm1],cost_type=1),\
lazy_greedy([hff2,hlm2],preferred=[hff2,hlm2]),\
lazy_wastar([hff2,hlm2],preferred=[hff2,hlm2],w=5),\
lazy_wastar([hff2,hlm2],preferred=[hff2,hlm2],w=3),\
lazy_wastar([hff2,hlm2],preferred=[hff2,hlm2],w=2),\
lazy_wastar([hff2,hlm2],preferred=[hff2,hlm2],w=1)],\
repeat_last=true)"\
"""

lama_noreas_hybrid = """\
--heuristic "hlm1,hff1=lm_ff_syn(lm_rhw(reasonable_orders=false,lm_cost_type=1,cost_type=1))" \
--heuristic "hlm2,hff2=lm_ff_syn(lm_rhw(reasonable_orders=false,lm_cost_type=2,cost_type=2))" \
--search "iterated([lazy_greedy([hff1,hlm1],preferred=[hff1,hlm1],cost_type=1),\
lazy_wastar([hff1,hlm1],preferred=[hff1,hlm1],w=5,cost_type=1),\
lazy_wastar([hff1,hlm1],preferred=[hff1,hlm1],w=3,cost_type=1),\
lazy_wastar([hff1,hlm1],preferred=[hff1,hlm1],w=2,cost_type=1),\
lazy_wastar([hff1,hlm1],preferred=[hff1,hlm1],w=1,cost_type=1),\
lazy_wastar([hff2,hlm2],preferred=[hff2,hlm2],w=1,cost_type=0)],\
repeat_last=true)"\
"""

blind = """\
--search "astar(blind())"\
"""

oa10000 = """\
--search "astar(merge_and_shrink(shrink_strategy=shrink_fh(max_states=10000)))"\
"""

oa50000 = """\
--search "astar(merge_and_shrink())"\
"""

oa100000 = """\
--search "astar(merge_and_shrink(shrink_strategy=shrink_fh(max_states=100000)))"\
"""

oa200000 = """\
--search "astar(merge_and_shrink(shrink_strategy=shrink_fh(max_states=200000)))"\
"""

pdb1000 = """\
--search "astar(pdb(max_states=1000))"\
"""

pdb2500 = """\
--search "astar(pdb(max_states=2500))"\
"""

pdb5000 = """\
--search "astar(pdb(max_states=5000))"\
"""

pdb10000 = """\
--search "astar(pdb(max_states=10000))"\
"""

pdb25000 = """\
--search "astar(pdb(max_states=25000))"\
"""

pdb50000 = """\
--search "astar(pdb(max_states=50000))"\
"""

pdb100000 = """\
--search "astar(pdb(max_states=100000))"\
"""

pdb250000 = """\
--search "astar(pdb(max_states=250000))"\
"""

pdb500000 = """\
--search "astar(pdb(max_states=500000))"\
"""

pdb1000000 = """\
--search "astar(pdb(max_states=1000000))"\
"""

pdb2500000 = """\
--search "astar(pdb(max_states=2500000))"\
"""

pdb5000000 = """\
--search "astar(pdb(max_states=5000000))"\
"""

pdb10000000 = """\
--search "astar(pdb(max_states=10000000))"\
"""

pdb25000000 = """\
--search "astar(pdb(max_states=25000000))"\
"""

pdb50000000 = """\
--search "astar(pdb(max_states=50000000))"\
"""

pdb100000000 = """\
--search "astar(pdb(max_states=100000000))"\
"""

pdb250000000 = """\
--search "astar(pdb(max_states=250000000))"\
"""

pdb500000000 = """\
--search "astar(pdb(max_states=500000000))"\
"""

pdb1000000000 = """\
--search "astar(pdb(max_states=1000000000))"\
"""

ipdb = """\
--search "astar(ipdb())"\
"""

ipdbi2 = """\
--search "astar(ipdb(min_improvement=2))"\
"""

ipdbi3 = """\
--search "astar(ipdb(min_improvement=3))"\
"""

ipdbi4 = """\
--search "astar(ipdb(min_improvement=4))"\
"""

ipdbi5 = """\
--search "astar(ipdb(min_improvement=5))"\
"""

ipdbi6 = """\
--search "astar(ipdb(min_improvement=6))"\
"""

ipdbi7 = """\
--search "astar(ipdb(min_improvement=7))"\
"""

ipdbi8 = """\
--search "astar(ipdb(min_improvement=8))"\
"""

ipdbi9 = """\
--search "astar(ipdb(min_improvement=9))"\
"""

ipdbi10 = """\
--search "astar(ipdb(min_improvement=10))"\
"""

ipdbi11 = """\
--search "astar(ipdb(min_improvement=11))"\
"""

ipdbi12 = """\
--search "astar(ipdb(min_improvement=12))"\
"""

ipdbi13 = """\
--search "astar(ipdb(min_improvement=13))"\
"""

ipdbi14 = """\
--search "astar(ipdb(min_improvement=14))"\
"""

ipdbi15 = """\
--search "astar(ipdb(min_improvement=15))"\
"""

ipdbi16 = """\
--search "astar(ipdb(min_improvement=16))"\
"""

ipdbi17 = """\
--search "astar(ipdb(min_improvement=17))"\
"""

ipdbi18 = """\
--search "astar(ipdb(min_improvement=18))"\
"""

ipdbi19 = """\
--search "astar(ipdb(min_improvement=19))"\
"""

ipdbi20 = """\
--search "astar(ipdb(min_improvement=20))"\
"""

pdbs = """\
--search "astar(cpdbs())"\
"""

ipdb_hhh = """\
--search "astar(ipdb())"\
"""

ipdb_hhh_pipesworld = """\
--search "astar(ipdb(num_samples=250,min_improvement=3))"\
"""

ipdb_hhh_airport = """\
--search "astar(ipdb(num_samples=50,min_improvement=5))"\
"""

gapdb = """\
--search "astar(gapdb())"\
"""

gapdb_e10 = """\
--search "astar(gapdb(num_episodes=10))"\
"""

gapdb_e20 = """\
--search "astar(gapdb(num_episodes=20))"\
"""

gapdb_e30 = """\
--search "astar(gapdb(num_episodes=30))"\
"""

gapdb_e40 = """\
--search "astar(gapdb(num_episodes=40))"\
"""

gapdb_e50 = """\
--search "astar(gapdb(num_episodes=50))"\
"""

gapdb_e60 = """\
--search "astar(gapdb(num_episodes=60))"\
"""

gapdb_e70 = """\
--search "astar(gapdb(num_episodes=70))"\
"""

gapdb_e80 = """\
--search "astar(gapdb(num_episodes=80))"\
"""

gapdb_e90 = """\
--search "astar(gapdb(num_episodes=90))"\
"""

gapdb_e100 = """\
--search "astar(gapdb(num_episodes=100))"\
"""

gapdb_max100 = """\
--search "astar(gapdb(pdb_max_size=100))"\
"""

gapdb_max1000 = """\
--search "astar(gapdb(pdb_max_size=1000))"\
"""

gapdb_max10000 = """\
--search "astar(gapdb(pdb_max_size=10000))"\
"""

gapdb_max100000 = """\
--search "astar(gapdb(pdb_max_size=100000))"\
"""

gapdb_max1000000 = """\
--search "astar(gapdb(pdb_max_size=1000000))"\
"""

gapdb_c10 = """\
--search "astar(gapdb(num_collections=10))"\
"""

gapdb_c20 = """\
--search "astar(gapdb(num_collections=20))"\
"""

gapdb_c40 = """\
--search "astar(gapdb(num_collections=40))"\
"""

gapdb_c80 = """\
--search "astar(gapdb(num_collections=80))"\
"""

gapdb_m5 = """\
--search "astar(gapdb(mutation_probability=5))"\
"""

gapdb_m10 = """\
--search "astar(gapdb(mutation_probability=10))"\
"""

gapdb_disjoint = """\
--search "astar(gapdb(disjoint=true))"
"""

gapdb_1 = """\
--search "astar(gapdb(pdb_max_size=1024,num_episodes=50,num_collections=5))"\
"""

gapdb_2 = """\
--search "astar(gapdb(pdb_max_size=32768,num_episodes=50,num_collections=5))"\
"""

gapdb_3 = """\
--search "astar(gapdb(pdb_max_size=1024,num_episodes=100,num_collections=5))"\
"""

gapdb_4 = """\
--search "astar(gapdb(pdb_max_size=32768,num_episodes=100,num_collections=5))"\
"""

gapdb_5 = """\
--search "astar(gapdb(pdb_max_size=1024,num_episodes=300,num_collections=5))"\
"""

gapdb_6 = """\
--search "astar(gapdb(pdb_max_size=32768,num_episodes=300,num_collections=5))"\
"""

gapdb_7 = """\
--search "astar(gapdb(pdb_max_size=32768,num_episodes=100,num_collections=10))"\
"""

gapdb_8 = """\
--search "astar(gapdb(pdb_max_size=32768,num_episodes=100,num_collections=15))"\
"""

gapdb_9 = """\
--search "astar(gapdb(pdb_max_size=1048576,num_episodes=100,num_collections=15))"\
"""

gapdb_10 = """\
--search "astar(gapdb(pdb_max_size=32768,num_episodes=300,num_collections=15))"\
"""

gapdb_11 = """\
--search "astar(gapdb(pdb_max_size=32768,num_episodes=100,num_collections=20))"\
"""

gapdb_12 = """\
--search "astar(gapdb(pdb_max_size=1048576,num_episodes=300,num_collections=20))"\
"""

gapdb_comparison = """\
--search "astar(gapdb(pdb_max_size=100000,num_episodes=100,num_collections=15))"\
"""

lmopt_rhw = """\
--search "astar(lmcount(lm_rhw(),admissible=true),mpd=true)"\
"""

lmopt_hm1 = """\
--search "astar(lmcount(lm_hm(m=1),admissible=true),mpd=true)"\
"""

lmopt_zg = """\
--search "astar(lmcount(lm_zg(),admissible=true),mpd=true)"\
"""

lmopt_rhw_hm1 = """\
--search "astar(lmcount(lm_merged([lm_rhw(),lm_hm(m=1)]),admissible=true),mpd=true)"\
"""

lmopt_rhw_zg = """\
--search "astar(lmcount(lm_merged([lm_rhw(),lm_zg()]),admissible=true),mpd=true)"\
"""

lmopt_hm1_zg = """\
--search "astar(lmcount(lm_merged([lm_zg(),lm_hm(m=1)]),admissible=true),mpd=true)"\
"""

lmopt_rhw_hm1_zg = """\
--search "astar(lmcount(lm_merged([lm_rhw(),lm_zg(),lm_hm(m=1)]),admissible=true),mpd=true)"\
"""


iter_ff = """\
--heuristic "h=ff(cost_type=1)" \
--search "iterated(lazy_greedy(h, preferred=h), repeat_last=true)"\
"""

seq_opt_fdss_1 = "ipc seq-opt-fdss-1 --plan-file sas_plan"


def _build_satisficing_configs(cost_types):
    result = []
    for search_type in ["lazy", "eager"]:
        for alg in ["greedy", "wa3"]:
            if alg.startswith("wa"):
                weight = int(alg[2:])
                extra_alg_opts = "w=%d," % weight
                realalg = "wastar"
            else:
                realalg = alg
                extra_alg_opts = ""

            for h in ["add", "cea", "cg", "ff"]:
                for cost_type in cost_types:
                    if cost_type == 2:
                        search_cost_type = 0
                    else:
                        search_cost_type = cost_type
                    name = "%s_%s_%s_%s" % (search_type, alg, h, cost_type)
                    args = [
                        "--heuristic",
                        "'h=%s(cost_type=%d)'" % (h, cost_type),
                        "--search",
                        ]
                    if (search_type, realalg) == ("eager", "wastar"):
                        args.append("'eager(single(sum([g(),weight(h,%d)])),preferred=h,cost_type=%d)'" % (weight, search_cost_type))
                    else:
                        args.append("'%s_%s(h,%spreferred=h,cost_type=%d)'" % (
                                search_type, realalg, extra_alg_opts, search_cost_type))
                    result.append((name, " ".join(args)))
    return result


def ipc_optimal():
    return [
        ("blind", "--search 'astar(blind())'"),
        ("hmax",  "--search 'astar(hmax())'"),
        ("lmcut", "--search 'astar(lmcut())'"),
        ("bjolp", lmopt_rhw_hm1),
        ("lmopt_rhw", lmopt_rhw),
        ("lmopt_hm1", lmopt_hm1),
        ("mas10000", '--search "astar(merge_and_shrink(shrink_strategy=shrink_fh(max_states=10000)))"'),
        ("mas50000", '--search "astar(merge_and_shrink(shrink_strategy=shrink_fh(max_states=50000)))"'),
        ("mas100000", '--search "astar(merge_and_shrink(shrink_strategy=shrink_fh(max_states=100000)))"'),
        ]


def satisficing_configs():
    return _build_satisficing_configs([0])


def satisficing_configs_with_costs():
    return _build_satisficing_configs([0, 1, 2])


def _alternation_config(kind, heurs):
    name = "alt_%s_%s" % (kind, "_".join(heurs))
    args = []
    for h in heurs:
        args.append("--heuristic")
        args.append("'h%s=%s(cost_type=1)'" % (h, h))
    args.append("--search")
    comma_string = ",".join("h%s" % h for h in heurs)
    args.append("'%s_greedy([%s],preferred=[%s],cost_type=1)'" % (
        kind, comma_string, comma_string))
    return name, " ".join(args)


def alternation_configs():
    result = []
    for kind in ["lazy", "eager"]:
        for l1 in [[], ["ff"]]:
            for l2 in [[], ["cea"]]:
                for l3 in [[], ["add"]]:
                    for l4 in [[], ["cg"]]:
                        heurs = l1 + l2 + l3 + l4
                        if len(heurs) >= 2:
                            result.append(_alternation_config(kind, heurs))
    return result


def raz_ipc():
    return [
        ("mas-1", "--search 'astar(merge_and_shrink(merge_strategy=merge_linear_reverse_level,shrink_strategy=shrink_bisimulation(max_states=infinity,threshold=1,greedy=true,initialize_by_h=false,group_by_h=false)))'"),
        ("mas-2", "--search 'astar(merge_and_shrink(merge_strategy=merge_linear_reverse_level,shrink_strategy=shrink_bisimulation(max_states=200000,greedy=false,initialize_by_h=true,group_by_h=true)))'"),
        ]


def lama11_unitcost():
    return [
        ("lama-unit-1", """\
--heuristic "hlm,hff=lm_ff_syn(lm_rhw(reasonable_orders=true))" \
--search "iterated([lazy_greedy([hff,hlm],preferred=[hff,hlm]),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=5),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=3),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=2),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=1)],\
repeat_last=true,continue_on_fail=true)"\
"""),

        ("lama-unit-2", """\
--heuristic "hlm,hff=lm_ff_syn(lm_rhw(reasonable_orders=true))" \
--search "iterated([lazy_greedy([hff,hlm],preferred=[hff,hlm],reopen_closed=true),\
lazy_wastar(hff,hlm,preferred=([hff,hlm],w=5),\
lazy_wastar(hff,hlm,preferred=([hff,hlm],w=3),\
lazy_wastar(hff,hlm,preferred=([hff,hlm],w=2),\
lazy_wastar(hff,hlm,preferred=([hff,hlm],w=1)],\
repeat_last=true)"\
"""),
        # Skip name lama-unit-3 to be consistent with lama-gen-X naming.
        ("lama-unit-4", """\
--heuristic "hlm,hff=lm_ff_syn(lm_rhw(reasonable_orders=true))" \
--search "iterated([
             eager(alt([single(hff),
                       single(hff,pref_only=true),
                       single(hlm),
                       single(hlm,pref_only=true)]),
                   preferred=[hff,hlm],reopen_closed=true),
             eager(alt([single(sum([g(),weight(hff,5)])),
                       single(sum([g(),weight(hff,5)]),pref_only=true),
                       single(sum([g(),weight(hlm,5)])),
                       single(sum([g(),weight(hlm,5)]),pref_only=true)]),
                   preferred=[hff,hlm],reopen_closed=true),
             eager(alt([single(sum([g(),weight(hff,3)])),
                       single(sum([g(),weight(hff,3)]),pref_only=true),
                       single(sum([g(),weight(hlm,3)])),
                       single(sum([g(),weight(hlm,3)]),pref_only=true)]),
                   preferred=[hff,hlm],reopen_closed=true),
             eager(alt([single(sum([g(),weight(hff,2)])),
                       single(sum([g(),weight(hff,2)]),pref_only=true),
                       single(sum([g(),weight(hlm,2)])),
                       single(sum([g(),weight(hlm,2)]),pref_only=true)]),
                   preferred=[hff,hlm],reopen_closed=true),
             eager(alt([single(sum([g(),weight(hff,1)])),
                       single(sum([g(),weight(hff,1)]),pref_only=true),
                       single(sum([g(),weight(hlm,1)])),
                       single(sum([g(),weight(hlm,1)]),pref_only=true)]),
                   preferred=[hff,hlm],reopen_closed=true),
             repeat_last=true)"\
"""),
        ]


def lama11_generalcost():
    return [
        ("lama-gen-1", """\
--heuristic "hlm,hff=lm_ff_syn(lm_rhw(reasonable_orders=true,lm_cost_type=2,cost_type=2))" \
--search "iterated([lazy_greedy([hff,hlm],preferred=[hff,hlm]),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=5),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=3),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=2),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=1)],\
repeat_last=true,continue_on_fail=true)"\
"""),

        ("lama-gen-2", """\
--heuristic "hlm,hff=lm_ff_syn(lm_rhw(reasonable_orders=true,lm_cost_type=2,cost_type=2))" \
--search "iterated([lazy_greedy([hff,hlm],preferred=[hff,hlm],reopen_closed=true),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=5),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=3),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=2),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=1)],\
repeat_last=true)"\
"""),

        ("lama-gen-3", """\
--heuristic "hlm1,hff1=lm_ff_syn(lm_rhw(reasonable_orders=true,lm_cost_type=1,cost_type=1))" \
--heuristic "hlm2,hff2=lm_ff_syn(lm_rhw(reasonable_orders=true,lm_cost_type=2,cost_type=2))" \
--search "iterated([lazy_greedy([hff1,hlm1],preferred=[hff1,hlm1],cost_type=1,reopen_closed=true),\
lazy_greedy([hff2,hlm2],preferred=[hff2,hlm2],reopen_closed=true),\
lazy_wastar([hff2,hlm2],preferred=[hff2,hlm2],w=5),\
lazy_wastar([hff2,hlm2],preferred=[hff2,hlm2],w=3),\
lazy_wastar([hff2,hlm2],preferred=[hff2,hlm2],w=2),\
lazy_wastar([hff2,hlm2],preferred=[hff2,hlm2],w=1)],\
repeat_last=true)"\
"""),

        ("lama-gen-4", """\
--heuristic "hlm,hff=lm_ff_syn(lm_rhw(reasonable_orders=true,lm_cost_type=2,cost_type=2))" \
--search "iterated([
             eager(alt([single(hff),
                       single(hff,pref_only=true),
                       single(hlm),
                       single(hlm,pref_only=true)]),
                   preferred=[hff,hlm],reopen_closed=true),
             eager(alt([single(sum([g(),weight(hff,5)])),
                       single(sum([g(),weight(hff,5)]),pref_only=true),
                       single(sum([g(),weight(hlm,5)])),
                       single(sum([g(),weight(hlm,5)]),pref_only=true)]),
                   preferred=[hff,hlm],reopen_closed=true),
             eager(alt([single(sum([g(),weight(hff,3)])),
                       single(sum([g(),weight(hff,3)]),pref_only=true),
                       single(sum([g(),weight(hlm,3)])),
                       single(sum([g(),weight(hlm,3)]),pref_only=true)]),
                   preferred=[hff,hlm],reopen_closed=true),
             eager(alt([single(sum([g(),weight(hff,2)])),
                       single(sum([g(),weight(hff,2)]),pref_only=true),
                       single(sum([g(),weight(hlm,2)])),
                       single(sum([g(),weight(hlm,2)]),pref_only=true)]),
                   preferred=[hff,hlm],reopen_closed=true),
             eager(alt([single(sum([g(),weight(hff,1)])),
                       single(sum([g(),weight(hff,1)]),pref_only=true),
                       single(sum([g(),weight(hlm,1)])),
                       single(sum([g(),weight(hlm,1)]),pref_only=true)]),
                   preferred=[hff,hlm],reopen_closed=true)],
             repeat_last=true)"\
"""),

        ("lama-gen-5", """\
--heuristic "hlm1,hff1=lm_ff_syn(lm_rhw(reasonable_orders=true,lm_cost_type=1,cost_type=1))" \
--heuristic "hlm2,hff2=lm_ff_syn(lm_rhw(reasonable_orders=true,lm_cost_type=2,cost_type=2))" \
--search "iterated([
             eager(alt([single(hff1),
                       single(hff1,pref_only=true),
                       single(hlm1),
                       single(hlm1,pref_only=true)]),
                   preferred=[hff1,hlm1],cost_type=1,reopen_closed=true),
             eager(alt([single(hff2),
                       single(hff2,pref_only=true),
                       single(hlm2),
                       single(hlm2,pref_only=true)]),
                   preferred=[hff2,hlm2],reopen_closed=true),
             eager(alt([single(sum([g(),weight(hff2,5)])),
                       single(sum([g(),weight(hff2,5)]),pref_only=true),
                       single(sum([g(),weight(hlm2,5)])),
                       single(sum([g(),weight(hlm2,5)]),pref_only=true)]),
                   preferred=[hff2,hlm2],reopen_closed=true),
             eager(alt([single(sum([g(),weight(hff2,3)])),
                       single(sum([g(),weight(hff2,3)]),pref_only=true),
                       single(sum([g(),weight(hlm2,3)])),
                       single(sum([g(),weight(hlm2,3)]),pref_only=true)]),
                   preferred=[hff2,hlm2],reopen_closed=true),
             eager(alt(single(sum(g(),weight(hff2,2))),
                       single(sum(g(),weight(hff2,2)),pref_only=true),
                       single(sum(g(),weight(hlm2,2))),
                       single(sum(g(),weight(hlm2,2)),pref_only=true)),
                   preferred=[hff2,hlm2],reopen_closed=true),
             eager(alt([single(sum([g(),weight(hff2,1)])),
                       single(sum([g(),weight(hff2,1)]),pref_only=true),
                       single(sum([g(),weight(hlm2,1)])),
                       single(sum([g(),weight(hlm2,1)]),pref_only=true)]),
                   preferred=[hff2,hlm2],reopen_closed=true)],
             repeat_last=true)"\
"""),
        ]


def astar_searches():
    return [('blind', blind), ('oa50000', oa50000)]


def ipc11():
    return [
        ('seq-sat-lama-2011-unit', """\
--heuristic "hlm,hff=lm_ff_syn(lm_rhw(reasonable_orders=true,lm_cost_type=2,cost_type=2))" \
--search "iterated([\
    lazy_greedy([hff,hlm],preferred=[hff,hlm]),\
    lazy_wastar([hff,hlm],preferred=[hff,hlm],w=5),\
    lazy_wastar([hff,hlm],preferred=[hff,hlm],w=3),\
    lazy_wastar([hff,hlm],preferred=[hff,hlm],w=2),\
    lazy_wastar([hff,hlm],preferred=[hff,hlm],w=1)],\
    repeat_last=true,continue_on_fail=true)"\
"""),
        ('seq-sat-lama-2011-nonunit', """\
--heuristic "hlm1,hff1=lm_ff_syn(lm_rhw(reasonable_orders=true,lm_cost_type=1,cost_type=1))" \
--heuristic "hlm2,hff2=lm_ff_syn(lm_rhw(reasonable_orders=true,lm_cost_type=2,cost_type=2))" \
--search "iterated([\
    lazy_greedy([hff1,hlm1],preferred=[hff1,hlm1],cost_type=1,reopen_closed=false),\
    lazy_greedy([hff2,hlm2],preferred=[hff2,hlm2],reopen_closed=false),\
    lazy_wastar([hff2,hlm2],preferred=[hff2,hlm2],w=5),\
    lazy_wastar([hff2,hlm2],preferred=[hff2,hlm2],w=3),\
    lazy_wastar([hff2,hlm2],preferred=[hff2,hlm2],w=2),\
    lazy_wastar([hff2,hlm2],preferred=[hff2,hlm2],w=1)],\
    repeat_last=true,continue_on_fail=true)"\
"""),
        ('seq-opt-fd-autotune', """\
--heuristic "hLMCut=lmcut()" \
--heuristic "hHMax=hmax()" \
--heuristic "hCombinedSelMax=selmax(\
    [hLMCut,hHMax],alpha=4,classifier=0,conf_threshold=0.85,\
    training_set=10,sample=0,uniform=true)" \
--search "astar(hCombinedSelMax,mpd=false,pathmax=true,cost_type=0)"\
"""),
        ('seq-opt-selmax', """\
--search "astar(selmax([lmcut(),lmcount(lm_merged([lm_hm(m=1),lm_rhw()]),admissible=true)],\
                       training_set=1000),mpd=true)"\
"""),
        ('seq-opt-bjolp', """\
--search "astar(lmcount(lm_merged([lm_rhw(),lm_hm(m=1)]),admissible=true),mpd=true)"\
"""),
        ('seq-opt-lmcut', """\
--search "astar(lmcut())"\
"""),]


# Used for debugging purposes
multiple_plans = """\
--heuristic "hlm,hff=lm_ff_syn(lm_rhw(reasonable_orders=false,lm_cost_type=2,cost_type=2))" \
--heuristic "hadd=add()" \
--search "iterated([lazy_greedy([hadd]),\
lazy_wastar([hff,hlm],preferred=[hff,hlm],w=2)],\
repeat_last=false)"\
"""


iterated_search = """\
--heuristic "hadd=add()" \
--search "iterated([lazy_greedy([hadd]),lazy_wastar([hadd])],\
repeat_last=false)"\
"""


def get_configs(configs_strings):
    """
    Parses configs_strings and returns a list of tuples of the form
    (configuration_name, configuration_string)

    config_strings can contain strings of the form
    "configs.py:cfg13" or "configs.py"
    """
    all_configs = []

    files_to_configs = defaultdict(list)
    for config_string in configs_strings:
        if ':' in config_string:
            config_file, config_name = config_string.split(':')
            config_file = os.path.abspath(config_file)
        else:
            # Check if this module has the config
            config_file, config_name = __file__, config_string

        files_to_configs[config_file].append(config_name)

    for file, config_names in files_to_configs.iteritems():
        module = tools.import_python_file(file)
        module_dict = module.__dict__
        for config_name in config_names:
            config_or_func = module_dict.get(config_name, None)
            if config_or_func is None:
                msg = 'Config "%s" could not be found in "%s"'
                logging.error(msg % (config_name, file))
                sys.exit()
            try:
                config_list = config_or_func()
            except TypeError:
                config_list = [(config_name, config_or_func)]

            all_configs.extend(config_list)

    logging.info('Found configs: %s' % all_configs)
    return all_configs


if __name__ == '__main__':
    get_configs(['blind', 'downward_configs:astar_searches'])
