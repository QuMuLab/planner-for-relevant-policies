

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

def load(pol, fmap):
    global POLICY

    print "\nLoading PRP policy..."

    with open(pol, 'r') as f:
        file_lines = filter(lambda x: x != '', [line.rstrip("\n") for line in f.readlines()])

    POLICY = []

    while file_lines:
        fluent_line = file_lines.pop(0)
        nfluents = set([fmap[f.strip().replace(',', '')[4:-1]] for f in \
                        filter(lambda x: 'not(' == x[:4], \
                               fluent_line.split(':')[-1][1:].split('/'))])
        pfluents = set([fmap[f.strip().replace(',', '')] for f in \
                        filter(lambda x: 'not(' != x[:4], \
                               fluent_line.split(':')[-1][1:].split('/'))])
        action = file_lines.pop(0).split(':')[-1].split('/')[0][1:-1].strip().replace(' ', '_')
        POLICY.append((nfluents, pfluents, action))

def next_action(s):
    global POLICY

    for (n,p,a) in POLICY:
        if 0 == len(n & s.fluents) and p <= s.fluents:
            return a

    return None
