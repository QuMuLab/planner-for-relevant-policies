
# Blocksworld
blocks = []
for i in range(1,31):
    blocks.append(("blocksworld/domain-fixed.pddl", "blocksworld/p%d.pddl" % i))


# FINAL
DOMAINS = {
    'blocksworld': blocks
}

