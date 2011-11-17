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
