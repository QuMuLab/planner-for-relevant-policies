"""
Example configurations taken from
http://alfons.informatik.uni-freiburg.de/downward/PlannerUsage
"""

# Eager A* search with landmark-cut heuristic (previously configuration ou)
ou = '--search "astar(lmcut())"'

fF = """\
--heuristic "hff=ff()" \
--search "lazy_greedy(hff, preferred=(hff))"\
"""

yY = """\
--heuristic "hcea=cea()" \
--search "lazy_greedy(hcea, preferred=(hcea))"\
"""

fFyY = """\
--heuristic "hff=ff()" --heuristic "hcea=cea()" \
--search "lazy_greedy(hff, hcea, preferred=(hff, hcea))"\
"""

blind = """\
--search "astar(blind())"\
"""

oa50000 = """\
--search "astar(mas())"\
"""
