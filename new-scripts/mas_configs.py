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
