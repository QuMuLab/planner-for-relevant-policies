def mas_mix():
    return [
        ("mas-1", "--search 'astar(mas(max_states=1,merge_strategy=5,shrink_strategy=shrink_bisimulation(true, false)))'"),
        ("mas-2", "--search 'astar(mas(max_states=200000,merge_strategy=5,shrink_strategy=shrink_dfp(Enable_Greedy_Bisimulation)))'"),
        ("mas-3", "--search 'astar(mas(shrink_strategy=shrink_fh(Low, Low)))'"),
        ("mas-4", "--search 'astar(mas(shrink_strategy=shrink_fh(High, Low)))'"),
       ("mas-5", "--search 'astar(mas(shrink_strategy=shrink_fh(Low, High)))'"),
       ("mas-6", "--search 'astar(mas(shrink_strategy=shrink_fh(High, High)))'"),
        ("mas-7", "--search 'astar(mas(shrink_strategy=shrink_dfp(Default)))'"),
        ("mas-8", "--search 'astar(mas(shrink_strategy=shrink_bisimulation(false,false)))'"),
        ("mas-9", "--search 'astar(mas(max_states=1000))'"),
]

