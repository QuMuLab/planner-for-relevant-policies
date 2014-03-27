

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
        fluents = set([fmap[f.strip().replace(',', '') + ')'] for f in file_lines.pop(0).split(':')[-1][1:].split(')')[:-1]])
        action = file_lines.pop(0).split(':')[-1].split('/')[0][1:-1].replace(' ', '_')
        POLICY.append((fluents, action))

def next_action(s):
    global POLICY

    for (p,a) in POLICY:
        if p <= s.fluents:
            return a

    return None
