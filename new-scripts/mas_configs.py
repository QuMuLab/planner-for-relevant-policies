def conf(a, b):
    return (a, b.replace("\n", ""))

def confs(*args):
    return [conf(*pair) for pair in args]

def conf_mas(name, mas_args):
    return conf("mas-%s" % name,
                "--search 'astar(merge_and_shrink(%s))'" % mas_args)

def conf_mas_hhh(max_states):
    if max_states % 1000 == 0:
        name = "hhh-%dk" % (max_states // 1000)
    else:
        name = "hhh-%d" % max_states
    return conf_mas(name,
                    "shrink_strategy=shrink_fh(max_states=%d)" % max_states)

def configs_mas_hhh():
    return [
        conf_mas_hhh(1000),
        conf_mas_hhh(10000),
        conf_mas_hhh(50000),
        conf_mas_hhh(100000),
        ]

def configs_mas_ipc_2011():
    return [
        conf_mas("mas-bisim",
                 """merge_strategy=merge_linear_reverse_level,
                    shrink_strategy=shrink_bisimulation(
                        max_states=infinity,
                        threshold=1,
                        greedy=true,
                        initialize_by_h=false,
                        group_by_h=false)"""),
        conf_mas("mas-dfp-200k",
                 """merge_strategy=merge_linear_reverse_level,
                    shrink_strategy=shrink_bisimulation(
                        max_states=200000,
                        threshold=200000,
                        greedy=false,
                        initialize_by_h=true,
                        group_by_h=true)"""),
        ]

def configs_mas_all():
    return configs_mas_hhh() + configs_mas_ipc_2011()

def configs_mas_ipc_2011():
    return [
        conf_mas("mas-bisim",
                 """merge_strategy=merge_linear_reverse_level,
                    shrink_strategy=shrink_bisimulation(
                        max_states=infinity,
                        threshold=1,
                        greedy=true,
                        initialize_by_h=false,
                        group_by_h=false)"""),
        conf_mas("mas-dfp-200k",
                 """merge_strategy=merge_linear_reverse_level,
                    shrink_strategy=shrink_bisimulation(
                        max_states=200000,
                        threshold=200000,
                        greedy=false,
                        initialize_by_h=true,
                        group_by_h=true)"""),
        ]


def abbrev(word):
    return "".join(part[0] for part in word.split("_"))


def abbrev_num(word):
    if word == "infinity":
        return "inf"
    num = int(word)
    if num % 1000 == 0:
        return "%dk" % (num // 1000)
    return str(num)


def no_limit_config(reduce_labels, greedy, merge_strategy):
    name = "%s-%s-%s" % (abbrev(reduce_labels), abbrev(greedy),
                         abbrev(merge_strategy))
    mas_args="""
        reduce_labels=%s,
        merge_strategy=%s,
        shrink_strategy=shrink_bisimulation(
            max_states=infinity,
            threshold=1,
            greedy=%s,
            initialize_by_h=false,
            group_by_h=false)
    """ % (reduce_labels, merge_strategy, greedy)
    config = "--search 'astar(merge_and_shrink(%s))'" % mas_args
    return conf(name, config)


def configs_selectivity_of_bisim():
    return [no_limit_config(reduce_labels=r,greedy=g,merge_strategy=m)
            for r in ["false", "true"]
            for g in ["false", "somewhat", "true"]
            for m in ["merge_linear_reverse_level", "merge_linear_cg_goal_level"]]


def configs_nonplain_bisimulation():
    return [no_limit_config(reduce_labels=r,greedy=g,merge_strategy=m)
            for r in ["false", "true"]
            for g in ["false", "somewhat", "true"]
            for m in ["merge_linear_reverse_level", "merge_linear_cg_goal_level"]
            if (r, g, m) != ("false", "false", "merge_linear_reverse_level")]


def config_plain_bisimulation():
    return [no_limit_config(reduce_labels="false",
                            greedy="false",
                            merge_strategy="merge_linear_reverse_level")]


def configs_mas_ipc_2011():
    return [
        conf_mas("mas-bisim",
                 """merge_strategy=merge_linear_reverse_level,
                    shrink_strategy=shrink_bisimulation(
                        max_states=infinity,
                        threshold=1,
                        greedy=true,
                        group_by_h=false)"""),
        conf_mas("mas-dfp-200k",
                 """merge_strategy=merge_linear_reverse_level,
                    shrink_strategy=shrink_bisimulation(
                        max_states=200000,
                        threshold=200000,
                        greedy=false,
                        initialize_by_h=true,
                        group_by_h=true)"""),
        ]


def config_jacm(merge_strategy, reduce_labels, greedy, bound, threshold):
    name = "M%s-R%s-G%s-B%s-T%s" % (
        abbrev(merge_strategy), abbrev(reduce_labels), abbrev(greedy),
        abbrev_num(bound), abbrev_num(threshold))
    mas_args = """
        reduce_labels=%s,
        merge_strategy=%s,
        shrink_strategy=shrink_bisimulation(
            max_states=%s,
            threshold=%s,
            greedy=%s,
            at_limit=return,
            group_by_h=false)
    """ % (reduce_labels, merge_strategy, bound, threshold, greedy)
    config = "--search 'astar(merge_and_shrink(%s))'" % mas_args
    return conf(name, config)


def config_jacm_hhh(merge_strategy, reduce_labels, bound):
    name = "M%s-R%s-HHH-B%s" % (
        abbrev(merge_strategy), abbrev(reduce_labels), abbrev_num(bound))
    mas_args = """
        reduce_labels=%s,
        merge_strategy=%s,
        shrink_strategy=shrink_fh(max_states=%s)
    """ % (reduce_labels, merge_strategy, bound)
    config = "--search 'astar(merge_and_shrink(%s))'" % mas_args
    return conf(name, config)


def configs_issue310():
    return [
        config_jacm(merge_strategy=m, reduce_labels=r, greedy=g,
                    bound=b, threshold=t)
        for m in ["merge_linear_reverse_level", "merge_linear_cg_goal_level"]
        for r in ["true"]
        for g in ["false", "legacy", "true"]
        for (t, b) in [(1, 100000), (1, "infinity"), (10000, 10000)]
        ]


def configs_jacm_test_label_reduction():
    return [
        config_jacm(merge_strategy=m, reduce_labels=r, greedy=g,
                    bound=b, threshold=t)
        for m in ["merge_linear_reverse_level", "merge_linear_cg_goal_level"]
        for r in ["false", "true"]
        for g in ["false", "true"]
        for (t, b) in [(1, 100000), (1, "infinity"), (10000, 10000)]
        ]


def configs_jacm_test_label_reduction_setdiff():
    # We don't include the issue310 configs here since we already computed
    # those separately.
    return set_difference(configs_jacm_test_label_reduction(),
                          configs_issue310())


def configs_jacm():
    return [
        config_jacm(merge_strategy=m, reduce_labels=r, greedy=g,
                    bound=b, threshold=t)
        for m in ["merge_linear_reverse_level", "merge_linear_cg_goal_level"]
        for r in ["true"]
        for g in ["false", "true"]
        for (t, b) in [
            (1, 10000), (1, 100000), (1, 200000), (1, "infinity"),
            (10000, 10000), (10000, 100000), (10000, 200000), (10000, "infinity"),
            (100000, 100000), (100000, 200000), (100000, "infinity"),
            (200000, 200000), (200000, "infinity"),
            ("infinity", "infinity"),
            ]]


def configs_jacm_setdiff():
    # We don't include the issue310 configs here since we already computed
    # those separately.
    return set_difference(configs_jacm(), configs_issue310())


def set_difference(configs1, configs2):
    configs2_dict = dict(configs2)
    return [(name, config) for (name, config) in configs1
            if name not in configs2_dict]


def configs_jacm_hhh_with_label_reduction():
    return [
        config_jacm_hhh(merge_strategy=m, reduce_labels=r, bound=b)
        for m in ["merge_linear_reverse_level", "merge_linear_cg_goal_level"]
        for r in ["true"]
        for b in [10000, 100000, 200000, "infinity"]
        ]


def config_ipdb(pdb_size, collection_size, samples, improvement):
    name = "PDBI-P%s-C%s-S%s-I%s" % (
        abbrev_num(pdb_size), abbrev_num(collection_size),
        samples, improvement)
    args = """
        pdb_max_size=%d,
        collection_max_size=%d,
        num_samples=%d,
        min_improvement=%d
    """ % (pdb_size, collection_size, samples, improvement)
    config = "--search 'astar(ipdb(%s))'" % args
    return conf(name, config)


def config_pdb(pdb_size):
    name = "PDB-%s" % abbrev_num(pdb_size)
    config = "--search 'astar(pdb(max_states=%d))'" % pdb_size
    return conf(name, config)


def config_combo_pdbs(pdb_size):
    name = "COMPDB-%s" % abbrev_num(pdb_size)
    config = "--search 'astar(zopdbs(combo=true,max_states=%d))'" % pdb_size
    return conf(name, config)


def config_pdbs_baseline():
    name = "PDBS-base"
    config = "--search 'astar(cpdbs())'"
    return conf(name, config)


def configs_jacm_ipdb():
    return [config_ipdb(p, c, s, i)
            for (p, c) in [
                (1000000, 10000000),
                (2000000, 20000000),
                (5000000, 50000000),
                (10000000, 100000000),
                ]
            for (s, i) in [
                (100, 1),
                (100, 10),
                (1000, 10),
                (1000, 100),
                ]
            ]


def configs_jacm_pdbs():
    return [config_pdb(p)
            for p in [
                100000,
                1000000,
                10000000,
                100000000,
                ]
            ] + [config_pdbs_baseline()]


def configs_jacm_combo_pdbs():
    return [config_combo_pdbs(p)
            for p in [
                100000,
                1000000,
                10000000,
                100000000,
                ]
            ]


def config_random(merge_strategy, bound):
    name = "RAND-M%s-B%s" % (abbrev(merge_strategy), abbrev_num(bound))
    mas_args = """
        merge_strategy=%s,
        shrink_strategy=shrink_random(max_states=%s)
    """ % (merge_strategy, bound)
    config = "--search 'astar(merge_and_shrink(%s))'" % mas_args
    return conf(name, config)


def configs_random():
    return [
        config_random(merge_strategy=m, bound=b)
        for m in ["merge_linear_reverse_level", "merge_linear_cg_goal_level"]
        for b in [100000]
        ]
