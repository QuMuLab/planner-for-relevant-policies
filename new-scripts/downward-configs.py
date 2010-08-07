"""
Example configurations taken from 
http://alfons.informatik.uni-freiburg.de/downward/PlannerUsage
"""

cfg1 = '--search "astar(lmcut())"'

cfg2 = """\
--heuristic "hff=ff()" --heuristic "hcea=cea()" \
--search "lazy_greedy(hff, hcea, preferred=(hff, hcea))"\
"""

cfg3 = """\
--heuristic "hff=ff()" --heuristic "hcea=cea()" \
--search "old_greedy(hff, hcea, preferred=(hff, hcea))"\
"""

