
# Blocksworld
blocks = []
for i in range(1,31):
    blocks.append(("blocksworld/domain-fixed.pddl", "blocksworld/p%d.pddl" % i))

blocks_orig = []
for i in range(1,31):
    blocks_orig.append(("blocksworld/domain.pddl", "blocksworld/p%d.pddl" % i))

# Faults
faults = []
for i in range(1,11):
    for j in range(1,i+1):
        faults.append(("faults/d_%d_%d-fixed.pddl" % (i,j), "faults/p_%d_%d.pddl" % (i,j)))

# First Responders
first = []
for i in range(1,11):
    for j in range(1,11):
        first.append(("first-responders/domain-fixed.pddl", "first-responders/p_%d_%d.pddl" % (i,j)))

# Forest
forest = []
for i in range(2,11):
    for j in range(1,11):
        forest.append(("forest/domain.pddl", "forest/p_%d_%d.pddl" % (i,j)))

# FINAL
DOMAINS = {
    'blocksworld': blocks,
    'blocksworld-orig': blocks_orig,
    'faults': faults,
    'first' : first,
    'forest' : forest
}

GOOD_DOMAINS = ['blocksworld', 'blocksworld-orig', 'first', 'forest']
