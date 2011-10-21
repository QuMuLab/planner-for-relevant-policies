from krrt.utils import get_file_list, read_file, write_file

domains = get_file_list('.', None, ['d_'])

for dom in domains:
    lines = read_file(dom)
    write_file('.'+''.join(dom.split('.')[:-1])+'-fixed.pddl', [lines[0]] + ["(:requirements :typing :strips :non-deterministic)"] + lines[1:])
