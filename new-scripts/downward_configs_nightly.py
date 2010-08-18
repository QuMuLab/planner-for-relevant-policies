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

lama = """\
--heuristic "hff=ff()" --heuristic "hlm=lmcount()" --search \
"iterated(lazy_wastar(hff,hlm,preferred=(hff,hlm),w=10),\
lazy_wastar(hff,hlm,preferred=(hff,hlm),w=5),\
lazy_wastar(hff,hlm,preferred=(hff,hlm),w=3),\
lazy_wastar(hff,hlm,preferred=(hff,hlm),w=2),\
lazy_wastar(hff,hlm,preferred=(hff,hlm),w=1),\
repeat_last=true)"\
"""

blind = """\
--search "astar(blind())"\
"""

oa50000 = """\
--search "astar(mas())"\
"""

