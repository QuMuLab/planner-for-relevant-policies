# Revisions:
'''
    "ff196fd6615f",
    # before issue211 branch -- h inadmissible for non-unit-cost!
    # doesn't have unified bisim yet

    "84153b1a11bd",
    # first admissible version; has unified bisim

    "e1b7d5effdd2",
    # got rid of DFP-gop; bug in computation of greed bisim fixed;
    # meaning of enable_greedy in unified_bisim has changed

    "91e8158f75d0",
    # Heavy refactoring
'''

def configs():
    CONFIGS = [
        ("mas-1-old", """--search 'astar(mas(
             max_states=1,
             merge_strategy=merge_linear_reverse_level,
             shrink_strategy=shrink_bisimulation(
               greedy=true,
               memory_limit=false)))'"""),

        ("mas-2-old", """--search 'astar(mas(
             max_states=200000,
             merge_strategy=merge_linear_reverse_level,
             shrink_strategy=shrink_dfp(
               style=enable_greedy_bisimulation)))'"""),

        ("mas-3-old", """--search 'astar(mas(
             max_states=200000,
             merge_strategy=merge_linear_reverse_level,
             shrink_strategy=shrink_dfp()))'"""),

        ("mas-1-new", """--search 'astar(mas(
             merge_strategy=merge_linear_reverse_level,
             shrink_strategy=shrink_bisimulation(
               max_states=1,
               greedy=true,
               memory_limit=false)))'"""),

        ("mas-2-new", """--search 'astar(mas(
             merge_strategy=merge_linear_reverse_level,
             shrink_strategy=shrink_dfp(
               max_states=200000,
               style=enable_greedy_bisimulation)))'"""),

        ("mas-3-new", """--search 'astar(mas(
             merge_strategy=merge_linear_reverse_level,
             shrink_strategy=shrink_dfp(
               max_states=200000)))'"""),

        ("mas-1b-new", """--search 'astar(mas(
              merge_strategy=merge_linear_reverse_level,
              shrink_strategy=shrink_unified_bisimulation(
                max_states=1,
                greedy=true,
                memory_limit=false)))'"""),

        # MAS_2B corresponds to the old DFP-bop; this is closer to MAS_2,
        # which is the old DFP-gop, than our "new" DFP-bop, which always
        # approximates bisimulation when asked to bisimulate. (The old heur
        # only approximated once exact bisimulation exceeded the bound.)

        ("mas-2b-new", """--search 'astar(mas(
              merge_strategy=merge_linear_reverse_level,
              shrink_strategy=shrink_unified_bisimulation(
                max_states=200000,
                greedy=false,
                memory_limit=true)))'"""),

        ("mas-2c-new", """--search 'astar(mas(
              merge_strategy=merge_linear_reverse_level,
              shrink_strategy=shrink_unified_bisimulation(
                max_states=200000,
                greedy=true,
                memory_limit=true)))'"""),

        ("mas-3b-new", """--search 'astar(mas(
              merge_strategy=merge_linear_reverse_level,
              shrink_strategy=shrink_unified_bisimulation(
                max_states=200000,
                greedy=false,
                memory_limit=true)))'"""),
        ]
    CONFIGS = [(a, b.replace("\n", "")) for a, b in CONFIGS]
    return CONFIGS
