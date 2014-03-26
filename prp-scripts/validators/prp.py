

POLICY = None

def load(pol, fmap):
    global POLICY

    print "\nLoading PRP policy..."

    with open(pol, 'r') as f:
        file_lines = filter(lambda x: x != '', [line.rstrip("\n") for line in f.readlines()])

    POLICY = []
    print fmap

    while file_lines:
        fluents = set([fmap[f] for f in file_lines.pop(0).split(':')[-1][1:].split(' ')])
        action = file_lines.pop(0).split(':')[-1].split('/')[0][1:-1].replace(' ', '_')
        POLICY.append((fluents, action))

def next_action(s):
    global POLICY
    print "\nFetching next action..."
    #return 'move-car_l-3-1_l-1-1'
    return 'move-car_l-1-1_l-2-1'
