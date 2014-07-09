
from fondparser import parser

p = parser.Problem('../fond-benchmarks/triangle-tireworld/domain.pddl', '../fond-benchmarks/triangle-tireworld/p1.pddl')
print p.actions[0].export()
