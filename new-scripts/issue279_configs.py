def conf(a, b):
    return (a, b.replace("\n", ""))

def conf_mas(name, mas_args):
    return conf("mas-%s" % name,
                "--search 'astar(merge_and_shrink(%s))'" % mas_args)

def conf_bisim(greediness):
    return conf_mas("bisim-%s" % greediness,
                    """merge_strategy=merge_linear_reverse_level,
                       shrink_strategy=shrink_bisimulation(
                           max_states=infinity,
                           threshold=1,
                           greedy=%s,
                           initialize_by_h=false,
                           group_by_h=false)""" % greediness)

def conf_dfp(n, greediness):
    assert n % 1000 == 0, n
    return conf_mas("dfp-%d-%s" % (n // 1000, greediness),
                    """merge_strategy=merge_linear_reverse_level,
                       shrink_strategy=shrink_bisimulation(
                           max_states=%d,
                           threshold=%d,
                           greedy=%s,
                           initialize_by_h=true,
                           group_by_h=true)""" % (n, n, greediness))

def configs_all():
    for greediness in ["false", "somewhat", "true"]:
        yield conf_bisim(greediness)
        for n in 10000, 100000, 200000:
            yield conf_dfp(n, greediness)
