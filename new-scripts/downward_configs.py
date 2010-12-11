"""
Example configurations taken from
http://alfons.informatik.uni-freiburg.de/downward/PlannerUsage
"""
import sys
import logging
from collections import defaultdict

import experiments
import tools
import downward_suites


HELP = """\
Comma separated list of configurations. They can be specified in the following \
ways: ou, astar_searches, myconfigfile:yY, myconfigfile:lama_configs.
The python modules have to live in the scripts dir.
"""

# Eager A* search with landmark-cut heuristic (previously configuration ou)
ou = '--search "astar(lmcut())"'

fF = """\
--heuristic "hff=ff()" \
--search "lazy_greedy(hff, preferred=(hff))"\
"""

yY = """\
--heuristic "hcea=cea()" \
--search "lazy_greedy(hcea, preferred=(hcea))"\
"""

yY_eager = """\
--heuristic "hcea=cea()" \
--search "eager_greedy(hcea, preferred=(hcea))"\
"""

fFyY = """\
--heuristic "hff=ff()" --heuristic "hcea=cea()" \
--search "lazy_greedy(hff, hcea, preferred=(hff, hcea))"\
"""

lama = """\
--heuristic "hff=ff()" --heuristic "hlm=lmcount()" --search \
"iterated(lazy_wastar(hff,hlm,preferred=(hff,hlm),w=10),\
lazy_wastar(hff,hlm,preferred=(hff,hlm),w=5),\
lazy_wastar(hff,hlm,preferred=(hff,hlm),w=3),\
lazy_wastar(hff,hlm,preferred=(hff,hlm),w=2),\
lazy_wastar(hff,hlm,preferred=(hff,hlm),w=1),\
repeat_last=true)"\
"""

blind = """\
--search "astar(blind())"\
"""

oa50000 = """\
--search "astar(mas())"\
"""

oa200000 = """\
--search "astar(mas(max_states=200000))"\
"""

pdb = """\
--search "astar(pdb())"\
"""


def astar_searches():
    return [('blind', blind), ('oa50000', oa50000)]

def arch_comp_configs():
    return [('blind', blind), ('oa200000', oa200000), ('yY', yY),
            ('yY_eager', yY_eager)]


def get_old_and_new_greedy(pairs):
    return pairs + [(nick.replace('lg', 'og'),
        config.replace('lazy_greedy', 'old_greedy')) for nick, config in pairs]


def issue158a():
    return get_old_and_new_greedy([
        ('lg_blind', '--search "lazy_greedy(blind())"'),
        ('lg_ff', '--search "lazy_greedy(ff())"'),
        ('lg_cea', '--search "lazy_greedy(cea())"'),
        ('lg_ff_cea', '--search "lazy_greedy(ff(), cea())"'),])

def issue158b():
    return get_old_and_new_greedy([
        ('lg_hff', '--heuristic hff=ff() '
            '--search "lazy_greedy(hff, preferred=(hff))"'),
        ('lg_hcea', '--heuristic "hcea=cea()" '
            '--search "lazy_greedy(hcea, preferred=(hcea))"'),
        ('lg_hff_hcea', '--heuristic "hff=ff()" --heuristic "hcea=cea()" '
            '--search "lazy_greedy(hff, hcea, preferred=(hff, hcea))"'),
        ('lg_hlm_hff', '--heuristic "hlm=lm_ff_syn(lm_rhw())" '
            '--heuristic "hff=ff()" '
            '--search "lazy_greedy(hlm, hff, preferred=(hlm, hff))"'),])




def get_configs(configs_strings):
    """
    Parses configs_strings and returns a list of tuples of the form
    (configuration_name, configuration_string)

    config_strings can contain strings of the form
    "configs.py:cfg13" or "configs.py"
    """
    all_configs = []

    files_to_configs = defaultdict(list)
    for config_string in configs_strings:
        if ':' in config_string:
            config_file, config_name = config_string.split(':')
        else:
            # Check if this module has the config
            config_file, config_name = __file__, config_string

        files_to_configs[config_file].append(config_name)

    for file, config_names in files_to_configs.iteritems():
        module = tools.import_python_file(file)
        module_dict = module.__dict__
        for config_name in config_names:
            config_or_func = module_dict.get(config_name, None)
            if config_or_func is None:
                msg = 'Config "%s" could not be found in "%s"' % (config_name, file)
                logging.error(msg)
                sys.exit()
            try:
                config_list = config_or_func()
            except TypeError:
                config_list = [(config_name, config_or_func)]

            all_configs.extend(config_list)

    logging.info('Found configs: %s' % all_configs)
    return all_configs


if __name__ == '__main__':
    get_configs(['blind', 'downward_configs:astar_searches'])

