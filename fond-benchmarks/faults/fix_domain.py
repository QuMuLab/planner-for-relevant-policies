import os

from krrt.utils import get_file_list, read_file, write_file, get_lines

domains = get_file_list('.', ['fixed', 'fip'], ['d_'])

print domains

for dom in domains:
    # Fix the original domain
    lines = read_file(dom)
    fixed_dom = '.'+''.join(dom.split('.')[:-1])+'-fixed.pddl'
    write_file(fixed_dom, [lines[0]] + ["(:requirements :typing :strips :non-deterministic)"] + lines[1:])
    
    # Fix the fip version
    preface = get_lines(dom, upper_bound = ':action')
    fixed_dom_fip = fixed_dom + '.fip'
    write_file(fixed_dom_fip, preface)
    
    print "python ../../src/translate/determinizer.py %s p_1_1.pddl >> %s" % (fixed_dom, fixed_dom_fip)
    os.system("python ../../src/translate/determinizer.py %s p_1_1.pddl >> %s" % (fixed_dom, fixed_dom_fip))
    os.system('echo ")" >> ' + fixed_dom_fip)
