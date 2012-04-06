def mas_mix():
    return [
        ("mas-1", "--search 'astar(merge_and_shrink(merge_strategy=merge_linear_reverse_level,shrink_strategy=shrink_bisimulation(max_states=infinity,threshold=1,greedy=true,initialize_by_h=false,group_by_h=false)))'"),
        ("mas-2", "--search 'astar(merge_and_shrink(merge_strategy=merge_linear_reverse_level,shrink_strategy=shrink_bisimulation(max_states=200000,greedy=false,initialize_by_h=true,group_by_h=true)))'"),
        ("mas-3", "--search 'astar(merge_and_shrink(shrink_strategy=shrink_fh(shrink_f=low,shrink_h=low)))'"),
        ("mas-4", "--search 'astar(merge_and_shrink(shrink_strategy=shrink_fh(shrink_f=high,shrink_h=low)))'"),
        ("mas-5", "--search 'astar(merge_and_shrink(shrink_strategy=shrink_random()))'"),
        ("mas-6", "--search 'astar(merge_and_shrink(shrink_strategy=shrink_fh(shrink_f=high,shrink_h=high)))'"),
        ("mas-7", "--search 'astar(merge_and_shrink(shrink_strategy=shrink_bisimulation(greedy=false,initialize_by_h=true,group_by_h=true)))'"),
        # Removed old strategy mas-8 because the parameter space for bisimulation-based strategies is now a bit different.
        ("mas-9", "--search 'astar(merge_and_shrink(shrink_strategy=shrink_fh(max_states=1000)))'"),
]

