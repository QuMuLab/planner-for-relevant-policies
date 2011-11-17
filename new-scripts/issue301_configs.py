def conf(a, b):
    return (a, b.replace("\n", ""))

def conf_mas(name, mas_args):
    return conf("mas-%s" % name,
                "--search 'astar(merge_and_shrink(%s))'" % mas_args)

def conf_bisim(greediness, merge_short, merge):
    return conf_mas("bisim-%s-%s" % (greediness, merge_short),
                    """merge_strategy=merge_%s,
                       shrink_strategy=shrink_bisimulation(
                           max_states=infinity,
                           threshold=1,
                           greedy=%s)""" % (merge, greediness))

def conf_dfp(n, greediness, merge_short, merge):
    assert n % 1000 == 0, n
    return conf_mas("dfp-%d-%s-%s" % (n // 1000, greediness, merge_short),
                    """merge_strategy=merge_%s,
                       shrink_strategy=shrink_bisimulation(
                           max_states=%d,
                           threshold=%d,
                           greedy=%s,
                           group_by_h=true)""" % (merge, n, n, greediness))

def configs(merge_short, merge):
    for greediness in ["false", "somewhat", "true"]:
        yield conf_bisim(greediness, merge_short, merge)
        for n in 10000, 100000, 200000:
            yield conf_dfp(n, greediness, merge_short, merge)


def configs_reverse_level():
    return configs("rl", "linear_reverse_level")

def configs_cg_goal_level():
    return configs("cgl", "linear_cg_goal_level")

def configs_goal_cg_level():
    return configs("gcl", "linear_goal_cg_level")
