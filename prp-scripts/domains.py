
DOMAIN_LOCATION = '../fond-benchmarks/'

# Blocksworld
blocks = []
redundant_blocks = {}
for i in range(1,31):
    blocks.append(("%s/blocksworld/domain-fixed.pddl" % DOMAIN_LOCATION, "%s/blocksworld/p%d.pddl" % (DOMAIN_LOCATION, i)))
for i in range(1,6):
    redundant_blocks[i] = [("%s/blocksworld/domain-redundant%d.pddl" % (DOMAIN_LOCATION, i), prob) for (dom,prob) in blocks]

blocks_orig = []
for i in range(1,31):
    blocks_orig.append(("%s/blocksworld/domain.pddl" % DOMAIN_LOCATION, "%s/blocksworld/p%d.pddl" % (DOMAIN_LOCATION, i)))

blocks_new = []
for i in range(1,51):
    blocks_new.append(("%s/blocksworld-new/domain.pddl" % DOMAIN_LOCATION, "%s/blocksworld-new/p%d.pddl" % (DOMAIN_LOCATION, i)))

blocks2 = []
for i in range(1,10):
    blocks2.append(("%s/blocksworld-2/domain.pddl" % DOMAIN_LOCATION, "%s/blocksworld-2/p0%d.pddl" % (DOMAIN_LOCATION, i)))
for i in range(10,16):
    blocks2.append(("%s/blocksworld-2/domain.pddl" % DOMAIN_LOCATION, "%s/blocksworld-2/p%d.pddl" % (DOMAIN_LOCATION, i)))

# Faults
faults = []
for i in range(1,11):
    for j in range(1,i+1):
        faults.append(("%s/faults/d_%d_%d-fixed.pddl" % (DOMAIN_LOCATION, i, j), "%s/faults/p_%d_%d.pddl" % (DOMAIN_LOCATION, i, j)))

# First Responders
first = []
for i in range(1,11):
    for j in range(1,11):
        first.append(("%s/first-responders/domain-fixed.pddl" % DOMAIN_LOCATION, "%s/first-responders/p_%d_%d.pddl" % (DOMAIN_LOCATION, i, j)))

first_new = []
for i in range(10,51,10):
    first_new.append(("%s/first-responders-new/domain-fixed.pddl" % DOMAIN_LOCATION, "%s/first-responders-new/p_%d_%d.pddl" % (DOMAIN_LOCATION, i, i)))
    for j in range(i-9,i):
        first_new.append(("%s/first-responders-new/domain-fixed.pddl" % DOMAIN_LOCATION, "%s/first-responders-new/p_%d_%d.pddl" % (DOMAIN_LOCATION, i, j)))
        first_new.append(("%s/first-responders-new/domain-fixed.pddl" % DOMAIN_LOCATION, "%s/first-responders-new/p_%d_%d.pddl" % (DOMAIN_LOCATION, j, i)))

# Forest
forest = []
for i in range(2,11):
    for j in range(1,11):
        forest.append(("%s/forest/domain.pddl" % DOMAIN_LOCATION, "%s/forest/p_%d_%d.pddl" % (DOMAIN_LOCATION, i, j)))

forest_new = []
for i in range(2,11):
    for j in range(1,11):
        forest_new.append(("%s/forest-new/domain.pddl" % DOMAIN_LOCATION, "%s/forest-new/p_%d_%d.pddl" % (DOMAIN_LOCATION, i, j)))


# Elevators
elevators = []
for i in range(1,10):
    elevators.append(("%s/elevators/domain.pddl" % DOMAIN_LOCATION, "%s/elevators/p0%d.pddl" % (DOMAIN_LOCATION, i)))
for i in range(10,16):
    elevators.append(("%s/elevators/domain.pddl" % DOMAIN_LOCATION, "%s/elevators/p%d.pddl" % (DOMAIN_LOCATION, i)))

# Zenotravel
zenotravel = []
for i in range(1,10):
    zenotravel.append(("%s/zenotravel/d0%d.pddl" % (DOMAIN_LOCATION, i), "%s/zenotravel/p0%d.pddl" % (DOMAIN_LOCATION, i)))
for i in range(10,16):
    zenotravel.append(("%s/zenotravel/d%d.pddl" % (DOMAIN_LOCATION, i), "%s/zenotravel/p%d.pddl" % (DOMAIN_LOCATION, i)))

# Triangle tireworld
triangle_tire = []
for i in range(1,41):
    triangle_tire.append(("%s/triangle-tireworld/domain.pddl" % DOMAIN_LOCATION, "%s/triangle-tireworld/p%d.pddl" % (DOMAIN_LOCATION, i)))

# Interesting (toy) domains
bus_fare = [("%s/interesting/bus-fare-domain.pddl" % DOMAIN_LOCATION, "%s/interesting/bus-fare-prob.pddl" % DOMAIN_LOCATION)]
climber = [("%s/interesting/climber-domain.pddl" % DOMAIN_LOCATION, "%s/interesting/climber-prob.pddl" % DOMAIN_LOCATION)]
river = [("%s/interesting/river-domain.pddl" % DOMAIN_LOCATION, "%s/interesting/river-prob.pddl" % DOMAIN_LOCATION)]


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
    'triangle-tire-test' : triangle_tire[0:2],
    'bus-fare' : bus_fare,
    'climber' : climber,
    'river' : river
}

REDUNDANT_DOMAINS = {
    'blocksworld': redundant_blocks
}

GOOD_DOMAINS = ['blocksworld', 'blocksworld-new', 'blocksworld-orig', 'first', 'forest', 'faults', 'triangle-tire']
FOND_DOMAINS = ['blocksworld-orig', 'first', 'forest', 'faults']
#NEW_DOMAINS = ['blocksworld-new', 'first-new', 'forest-new']
NEW_DOMAINS = ['blocksworld-new', 'forest-new']
IPC06_DOMAINS = ['blocksworld-2', 'elevators', 'zenotravel']
TEST_DOMAINS = ['blocksworld-test', 'first-test', 'forest-test', 'faults-test', 'triangle-tire-test']
INTERESTING_DOMAINS = ['triangle-tire', 'bus-fare', 'climber', 'river']

