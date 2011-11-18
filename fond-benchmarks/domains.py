
# Blocksworld
blocks = []
redundant_blocks = {}
for i in range(1,31):
    blocks.append(("blocksworld/domain-fixed.pddl", "blocksworld/p%d.pddl" % i))
for i in range(1,6):
    redundant_blocks[i] = [("blocksworld/domain-redundant%d.pddl" % i, prob) for (dom,prob) in blocks]

blocks_orig = []
for i in range(1,31):
    blocks_orig.append(("blocksworld/domain.pddl", "blocksworld/p%d.pddl" % i))

blocks_new = []
for i in range(1,51):
    blocks_new.append(("blocksworld-new/domain.pddl", "blocksworld-new/p%d.pddl" % i))

blocks2 = []
for i in range(1,10):
    blocks2.append(("blocksworld-2/domain.pddl", "blocksworld-2/p0%d.pddl" % i))
for i in range(10,16):
    blocks2.append(("blocksworld-2/domain.pddl", "blocksworld-2/p%d.pddl" % i))    

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

first_new = []
for i in range(10,51,10):
    first_new.append(("first-responders-new/domain-fixed.pddl", "first-responders-new/p_%d_%d.pddl" % (i,i)))
    for j in range(i-9,i):
        first_new.append(("first-responders-new/domain-fixed.pddl", "first-responders-new/p_%d_%d.pddl" % (i,j)))
        first_new.append(("first-responders-new/domain-fixed.pddl", "first-responders-new/p_%d_%d.pddl" % (j,i)))

# Forest
forest = []
for i in range(2,11):
    for j in range(1,11):
        forest.append(("forest/domain.pddl", "forest/p_%d_%d.pddl" % (i,j)))

forest_new = []
for i in range(2,11):
    for j in range(1,11):
        forest_new.append(("forest-new/domain.pddl", "forest-new/p_%d_%d.pddl" % (i,j)))


# Elevators
elevators = []
for i in range(1,10):
    elevators.append(("elevators/domain.pddl", "elevators/p0%d.pddl" % i))
for i in range(10,16):
    elevators.append(("elevators/domain.pddl", "elevators/p%d.pddl" % i))

# Zenotravel
zenotravel = []
for i in range(1,10):
    zenotravel.append(("zenotravel/domain.pddl", "zenotravel/p0%d.pddl" % i))
for i in range(10,16):
    zenotravel.append(("zenotravel/domain.pddl", "zenotravel/p%d.pddl" % i))

# Triangle tireworld
triangle_tire = []
for i in range(1,26):
    triangle_tire.append(("triangle-tireworld/domain.pddl", "triangle-tireworld/p%d.pddl" % i))

# FINAL
DOMAINS = {
    'blocksworld': blocks,
    'blocksworld-test': blocks_orig[0:2],
    'blocksworld-new': blocks_new,
    'blocksworld-orig': blocks_orig,
    'blocksworld-2': blocks2,
    'faults': faults,
    'faults-test': faults[0:2],
    'first' : first,
    'first-new' : first_new,
    'first-test' : first[0:2],
    'forest' : forest,
    'forest-new' : forest_new,
    'forest-test' : forest_new[0:2],
    'elevators' : elevators,
    'zenotravel' : zenotravel,
    'triangle-tire' : triangle_tire,
    'triangle-tire-test' : triangle_tire[0:2]
}

REDUNDANT_DOMAINS = {
    'blocksworld': redundant_blocks
}

GOOD_DOMAINS = ['blocksworld', 'blocksworld-new', 'blocksworld-orig', 'first', 'forest', 'faults']
FOND_DOMAINS = ['blocksworld-orig', 'first', 'forest', 'faults']
NEW_DOMAINS = ['blocksworld-new', 'first-new', 'forest-new']
IPC06_DOMAINS = ['blocksworld-2', 'elevators', 'zenotravel']
TEST_DOMAINS = ['blocksworld-test', 'first-test', 'forest-test', 'faults-test', 'triangle-tire-test']
INTERESTING_DOMAINS = ['triangle-tire']

