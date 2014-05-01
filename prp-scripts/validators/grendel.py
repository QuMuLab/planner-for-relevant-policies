

POLICY = None


def _translate_grendel_fluent(f):
    name = f.split('(')[-1].split(')')[0].split('_')[0]
    args = f.split('(')[-1].split(')')[0].split('_')[1:]
    return "%s(%s)" % (name, ' '.join(args))


def load(pol, fmap):
    global POLICY

    print "\nLoading GRENDEL policy..."

    with open(pol, 'r') as f:
        file_lines = filter(lambda x: x != '', [line.rstrip("\n") for line in f.readlines()])

    POLICY = []

    while file_lines:
        assert '(:policy-rule' == file_lines.pop(0)
        fluent_line = file_lines.pop(0).replace(') (', ')/(')
        action_line = file_lines.pop(0)
        assert ')' == file_lines.pop(0)

        nfluents = set([fmap[_translate_grendel_fluent(f)] for f in \
                        filter(lambda x: '(not' == x[:4], \
                               fluent_line.split('(and ')[-1][:-1].split('/'))])

        pfluents = set([fmap[_translate_grendel_fluent(f)] for f in \
                        filter(lambda x: '(not' != x[:4], \
                               fluent_line.split('(and ')[-1][:-1].split('/'))])

        action = action_line.split(':action ')[-1][1:-1].strip().replace(' ', '_')
        POLICY.append((nfluents, pfluents, action))

def next_action(s):
    global POLICY

    for (n,p,a) in POLICY:
        if 0 == len(n & s.fluents) and p <= s.fluents:
            return a

    return None
