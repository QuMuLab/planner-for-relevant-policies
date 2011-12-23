def conf(a, b):
    return (a, " ".join(b.split()))


def general_or_unit_cost(config_part, kind):
    # TODO: Need to declare multiple copies of the heuristics!
    if kind == "general":
        cost_type_search = "normal"
        cost_type_h = "plusone"
    elif kind == "unit":
        cost_type_search = "one"
        cost_type_h = "one"
    else:
        raise ValueError(kind)
    config_part = config_part.replace("COST_TYPE_SEARCH", cost_type_search)
    config_part = config_part.replace("COST_TYPE_H", cost_type_h)
    return config_part


def iterated(heuristics, search, schedule):
    ## TODO: Add cost type stuff. Must think about it at this level
    ## to know which heuristics to declare. Strategy: build heuristic strings,
    ## filter duplicates, use consistent naming conventions to allow
    ## search/replacing heuristic name strings easily.
    start = '--search "iterated(['
    parts = []
    collected_heuristics = []
    kinds_seen = set()

    if not isinstance(heuristics, str):
        heuristics = " ".join(heuristics)

    for kind, weight in schedule:
        if kind not in kinds_seen:
            kinds_seen.add(kind)
            collected_heuristics.append(general_or_unit_cost(heuristics, kind))
        part = general_or_unit_cost(search, kind)
        if weight is None:
            part = part.replace("GREEDY_OR_WASTAR", "greedy")
            part = part.replace("SEARCH_OPTS", "reopen_closed=false")
        else:
            part = part.replace("GREEDY_OR_WASTAR", "wastar")
            part = part.replace("SEARCH_OPTS", "w=%d" % weight)
        parts.append(part)
    end = '],repeat_last=true,continue_on_fail=true)"'
    heur = " ".join(collected_heuristics)
    search = start + ",".join(parts) + end
    return heur + " " + search


def heur_decl(heur_id, heur_name, *heur_opts):
    opts = heur_opts + ("cost_type=COST_TYPE_H",)
    return  '--heuristic "%s_COST_TYPE_H=%s(%s)"' % (
        heur_id, heur_name, ",".join(opts))


def syn_decl(lm_name, ff_name):
    return ('--heuristic "hlm_COST_TYPE_H,hff_COST_TYPE_H=lm_ff_syn(lm_rhw('
            'reasonable_orders=true,lm_cost_type=COST_TYPE_H,cost_type=COST_TYPE_H))"')


def search_decl(*heurs, **kwargs):
    preferred_heurs = kwargs.pop("preferred", None)
    if preferred_heurs is None:
        # If keyword arg is omitted, use all heuristics for preferred ops.
        preferred_heurs = heurs
    if kwargs:
        raise ValueError(kwargs)
    heurs = ",".join("%s_COST_TYPE_H" % h for h in heurs)
    preferred_heurs = ",".join("%s_COST_TYPE_H" % h for h in preferred_heurs)
    return "lazy_GREEDY_OR_WASTAR([%s],preferred=[%s],SEARCH_OPTS)" % (
        heurs, preferred_heurs)


LM_RHW = "lm_rhw(reasonable_orders=true,lm_cost_type=COST_TYPE_H,cost_type=COST_TYPE_H)"


UNIT_SCHEDULE = [ # weight and algorithm schedule used for unit-cost problems
    ("general", None),
    ("general", 5),
    ("general", 3),
    ("general", 2),
    ("general", 1),
    ]


GENERAL_SCHEDULE = [ # weight and algorithm schedule used for general-cost problems
    ("unit", None),
    ] + UNIT_SCHEDULE


## Planner versions for general-cost problems.

lama_general = conf("lama", iterated(
        syn_decl("hlm", "hff"),
        search_decl("hlm", "hff"),
        GENERAL_SCHEDULE))

lama_nosyn_general = conf("lama-nosyn", iterated(
        [heur_decl("hlm", "lmcount", LM_RHW, "pref=true"),
         heur_decl("hff", "ff")],
        search_decl("hlm", "hff"),
        GENERAL_SCHEDULE))

lama_limpref_general = conf("lama-limpref", iterated(
        [heur_decl("hlm", "lmcount", LM_RHW, "pref=false"),
         heur_decl("hff", "ff")],
        search_decl("hlm", "hff", preferred=["hff"]),
        GENERAL_SCHEDULE))

lama_nopref_general = conf("lama-nopref", iterated(
        [heur_decl("hlm", "lmcount", LM_RHW, "pref=false"),
         heur_decl("hff", "ff")],
        search_decl("hlm", "hff", preferred=[]),
        GENERAL_SCHEDULE))

lama_nolm_general = conf("lama-nolm", iterated(
        heur_decl("hff", "ff"),
        search_decl("hff"),
        GENERAL_SCHEDULE))

lama_nolm_nopref_general = conf("lama-nolm-nopref", iterated(
        heur_decl("hff", "ff"),
        search_decl("hff", preferred=[]),
        GENERAL_SCHEDULE))

## Planner versions for unit-cost problems.
## Have same nicknames as general-cost versions to allow result merging.

lama_unit = conf("lama", iterated(
        syn_decl("hlm", "hff"),
        search_decl("hlm", "hff"),
        UNIT_SCHEDULE))

lama_nosyn_unit = conf("lama-nosyn", iterated(
        [heur_decl("hlm", "lmcount", LM_RHW, "pref=true"),
         heur_decl("hff", "ff")],
        search_decl("hlm", "hff"),
        UNIT_SCHEDULE))

lama_limpref_unit = conf("lama-limpref", iterated(
        [heur_decl("hlm", "lmcount", LM_RHW, "pref=false"),
         heur_decl("hff", "ff")],
        search_decl("hlm", "hff", preferred=["hff"]),
        UNIT_SCHEDULE))

lama_nopref_unit = conf("lama-nopref", iterated(
        [heur_decl("hlm", "lmcount", LM_RHW, "pref=false"),
         heur_decl("hff", "ff")],
        search_decl("hlm", "hff", preferred=[]),
        UNIT_SCHEDULE))

lama_nolm_unit = conf("lama-nolm", iterated(
        heur_decl("hff", "ff"),
        search_decl("hff"),
        UNIT_SCHEDULE))

lama_nolm_nopref_unit = conf("lama-nolm-nopref", iterated(
        heur_decl("hff", "ff"),
        search_decl("hff", preferred=[]),
        UNIT_SCHEDULE))


## TODO: Add configurations with eager instead of lazy search.
##       Should deal with issue311 first.


def lamalike_general():
    return [
        lama_general,
        lama_nosyn_general,
        lama_limpref_general,
        lama_nopref_general,
        lama_nolm_general,
        lama_nolm_nopref_general,
        ]


def lamalike_unit():
    return [
        lama_unit,
        lama_nosyn_unit,
        lama_limpref_unit,
        lama_nopref_unit,
        lama_nolm_unit,
        lama_nolm_nopref_unit,
        ]


if __name__ == "__main__":
    print "general:"
    for pair in lamalike_general():
        print "%s: %s" % pair
    print "unit:"
    for pair in lamalike_unit():
        print "%s: %s" % pair
