import os
import sys
import shutil
import re
from optparse import OptionParser, OptionValueError, BadOptionError, Option

def divide_list(seq, size):
    '''
    >>> divide_list(range(10), 4)
    [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]
    '''
    return [seq[i:i+size] for i  in range(0, len(seq), size)]
    

def overwrite_dir(dir):
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.makedirs(dir)
    
def natural_sort(alist):
    """Sort alist alphabetically, but special-case numbers to get
    file2.txt before file10.ext."""
    def to_int_if_number(text):
        if text.isdigit():
            return int(text)
        else:
            return text
    def extract_numbers(text):
        parts = re.split("([0-9]+)", text)
        return map(to_int_if_number, parts)
    alist.sort(key=extract_numbers)


def listdir(path):
    return [filename for filename in os.listdir(path)
            if filename != ".svn"]


def find_file(basenames, dir="."):
    for basename in basenames:
        path = os.path.join(dir, basename)
        if os.path.exists(path):
            return path
    raise IOError("none found in %r: %r" % (dir, basenames))

class ExtOption(Option):
    '''
    This extended option allows comma-separated commandline options
    Strings that represent integers are automatically converted to ints
    
    Example:
    python myprog.py -a foo,bar -b aha -a oho,3
    '''

    ACTIONS = Option.ACTIONS + ("extend",)
    STORE_ACTIONS = Option.STORE_ACTIONS + ("extend",)
    TYPED_ACTIONS = Option.TYPED_ACTIONS + ("extend",)
    ALWAYS_TYPED_ACTIONS = Option.ALWAYS_TYPED_ACTIONS + ("extend",)
    
    def try_str_to_int(self, string):
        try:
            integer = int(string)
            return integer
        except ValueError:
            return string

    def convert_list(self, list):
        return map(self.try_str_to_int, list)

    def take_action(self, action, dest, opt, value, values, parser):
        if action == "extend":
            lvalue = value.split(",")
            values.ensure_value(dest, []).extend(self.convert_list(lvalue))
        else:
            Option.take_action(
                self, action, dest, opt, value, values, parser)
