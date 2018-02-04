

################################################################
##
##  Note: It is assumed that the policy file
##        is already translated using the
##        translate_policy.py script. For
##        example, in the directory used to
##        run prp with --dump-policy 2 used,
##        this would generate the right file:
##
##          python translate_policy.py > policy-final.out
##
###########################################################




POLICY = None
FSAP = None

def load(pol, fmap):
    global POLICY
    global FSAP

    print "\nLoading PRP policy..."

    with open(pol, 'r') as f:
        file_lines = filter(lambda x: x != '', [line.rstrip("\n") for line in f.readlines()])

    POLICY = []
    FSAP = {}

    STAGE_MAP = 0
    STAGE_POL = 1
    STAGE_FSAP = 2

    stage = STAGE_MAP

    while file_lines:
        fluent_line = file_lines.pop(0)

        if fluent_line == 'Policy:':
            stage = STAGE_POL
            continue
        elif fluent_line == 'FSAP:':
            stage = STAGE_FSAP
            continue
        elif stage == STAGE_MAP:
            continue

        nfluents = set([fmap[f.strip().replace(',', '')[4:-1]] for f in \
                        filter(lambda x: 'not(' == x[:4], \
                               fluent_line.split(':')[-1][1:].split('/'))])
        pfluents = set([fmap[f.strip().replace(',', '')] for f in \
                        filter(lambda x: ('not(' != x[:4]) and (len(x) > 0), \
                               fluent_line.split(':')[-1][1:].split('/'))])
        action = file_lines.pop(0).split(':')[-1].split('/')[0][1:-1].strip().replace(' ', '_')

        if STAGE_POL == stage:
            POLICY.append((nfluents, pfluents, action))
        elif STAGE_FSAP == stage:
            FSAP[action] = FSAP.get(action, []) + [(nfluents, pfluents)]
        else:
            assert False, "Error: Bad stage %d" % stage

def next_action(s):
    global POLICY
    global FSAP

    for (n,p,a) in POLICY:
        if 0 == len(n & s.fluents) and p <= s.fluents:
            ok = True
            for (n2,p2) in FSAP.get(a, []):
                if 0 == len(n2 & s.fluents) and p2 <= s.fluents:
                    ok = False
            if ok:
                return a

    return None
