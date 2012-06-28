
from krrt.utils import get_lines, read_file

index = 0
var_lines = get_lines('output', lower_bound = 'end_metric', upper_bound = 'begin_state')

num_vars = int(var_lines[index])
index += 1

def parse_var(lines, index):
    
    assert 'begin_variable' == lines[index]
    index += 1
    
    name = lines[index]
    index += 1
    
    assert '-1' == lines[index]
    index += 1
    
    num_vals = int(lines[index])
    index += 1
    
    vals = []
    for i in range(num_vals):
        vals.append(lines[index].split('Atom ')[-1])
        index += 1
    
    assert 'end_variable' == lines[index]
    index += 1
    
    if 2 == len(vals):
        if '<none of those>' == vals[0]:
            vals[0] = "!%s" % vals[1]
        elif '<none of those>' == vals[1]:
            vals[1] = "!%s" % vals[0]
    
    return (name, vals, index)


mapping = {}

for i in range(num_vars):
    (name, vals, index) = parse_var(var_lines, index)
    for j in range(len(vals)):
        mapping["%s:%s" % (name, j)] = vals[j]

policy_lines = read_file('policy.out')
new_lines = []
for line in policy_lines:
    if 'If' == line[:2]:
        print "If holds: %s" % ' '.join([mapping[item] for item in line.split(' ')[2:]])
    else:
        print line

#print mapping


