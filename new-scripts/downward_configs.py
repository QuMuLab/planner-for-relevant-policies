"""
Example configurations taken from 
http://alfons.informatik.uni-freiburg.de/downward/PlannerUsage
"""
import logging
from collections import defaultdict

import experiments

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


def get_configs(configs_strings):
    """
    Parses configs_strings and returns a list of tuples of the form 
    (configuration_name, configuration_string)
    
    config_strings can contain strings of the form 
    "configs.py:cfg13" or "configs.py"
    """
    def parse_configs(file):
        assert file.endswith('.py')
        module_name = file[:-3]
        try:
            module = __import__(module_name)
        except ImportError, err:
            logging.error('File "%s" could not be imported' % file)
            sys.exit(1)
        config_names = [c for c in dir(module) if not c.startswith('_')]
        configs = [(name, getattr(module, name)) for name in config_names]
        # We only want strings, no functions or imported modules
        configs = filter(lambda (name, config): type(config) == str, configs)
        return configs
        
    all_configs = []
        
    complete_files = []
    files_to_configs = defaultdict(list)
    for config_string in configs_strings:
        if ':' in config_string:
            config_file, config_name = config_string.split(':')
            files_to_configs[config_file].append(config_name)
        elif config_string.endswith('.py'):
                # We have a complete file
                complete_files.append(config_string)
        else:
            # Check if this module has the config
            config = globals().get(config_string, None)
            if config is not None:
                all_configs.append((config_string, config))
            else:
                print 'Config "%s" could not be found' % config_string
    
    
    for file in complete_files:
        all_configs.extend(parse_configs(file))
    
    for file, config_names in files_to_configs.iteritems():
        if file in complete_files:
            # We have already imported this file
            continue
        filtered_configs = [(name, c) for (name, c) in parse_configs(file) \
                            if name in config_names]
        found = [name for (name, c) in filtered_configs]
        not_found = [n for n in config_names if n not in found]
        if not_found:
            logging.error('The configs %s were not found in "%s"' % (not_found, file))
            sys.exit(1)
        all_configs.extend(filtered_configs)
    
    logging.info('Found configs: %s' % all_configs)
    return all_configs
    
    
def get_dw_parser():
    '''
    Returns a parser for fast-downward experiments
    '''
    # We can add our own commandline parameters
    dw_parser = experiments.ExpArgParser()
    dw_parser.add_argument('-s', '--suite', default=[], nargs='+', 
                            required=True, help='tasks, domains or suites')
    dw_parser.add_argument('-c', '--configs', default=[], nargs='+', 
                            required=True, 
                            help='e.g. "configs.py:cfg13" or "configs.py"')
    return dw_parser

