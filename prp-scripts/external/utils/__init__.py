# The following modules are the available utils
from experimentation import get_value, match_value, get_lines, run_experiment, run_command
from fileio import read_file, write_file, append_file, load_CSV, save_CSV

#####################
# General Utilities #
#####################

def get_file_list(dir_name, forbidden_list = None, match_list = None):
    import os
    
    forbidden_patterns = ['.svn']
    
    file_list = [os.path.join(dir_name, item) for item in os.listdir(dir_name)]
    
    if forbidden_list:
        forbidden_patterns.extend(forbidden_list)
    
    for item in forbidden_patterns:
        file_list = filter(lambda x: item not in x, file_list)
    
    if match_list:
        for match_item in match_list:
            file_list = filter(lambda x:match_item in x, file_list)
    
    return file_list

def get_opts():
    import sys
    argv = sys.argv
    
    opts = {}
    flags = []
    
    while argv:
        if argv[0][0] == '-':                  # find "-name value" pairs
            opts[argv[0]] = argv[1]            # dict key is "-name" arg
            argv = argv[2:]                    
        else:
            flags.append(argv[0])
            argv = argv[1:]
    return opts, flags


