"""
Example configurations taken from 
http://alfons.informatik.uni-freiburg.de/downward/PlannerUsage
"""

# Eager A* search with landmark-cut heuristic (previously configuration ou)
cfg1 = '--search "astar(lmcut())"'


# Lazy greedy best first search with FF and context-enhanced additive 
# heuristic, using preferred operators of both heuristics 
# (same configuration as previous option fFyY but using the new general 
# search implementation)
"""
cfg2 = """\
--heuristic "hff=ff()" --heuristic "hcea=cea()" \
--search "lazy_greedy(hff, hcea, preferred=(hff, hcea))"\
"""

cfg3 = """\
--heuristic "hff=ff()" --heuristic "hcea=cea()" \
--search "old_greedy(hff, hcea, preferred=(hff, hcea))"\
"""

