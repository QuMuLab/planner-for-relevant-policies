import os
import sys
import shutil
import subprocess
import re
import logging
import traceback
from shutil import *
from collections import MutableMapping

from external import argparse
from external.configobj import ConfigObj


LOG_LEVEL = None


def prod(values):
    """Computes the product of a list of numbers.

    >>> print prod([2, 3, 7])
    42
    """
    assert len(values) >= 1
    prod = 1
    for value in values:
        prod *= value
    return prod


def divide_list(seq, size):
    """
    >>> divide_list(range(10), 4)
    [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9]]
    """
    return [seq[i:i+size] for i  in range(0, len(seq), size)]
    
    
def makedirs(dir):
    """
    mkdir variant that does not complain when the dir already exists
    """
    if not os.path.exists(dir):
        os.makedirs(dir)
    

def overwrite_dir(dir):
    if os.path.exists(dir):
        if not os.path.exists(os.path.join(dir, 'run')):
            msg = 'The experiment directory "%s" ' % dir
            msg += 'is not empty, do you want to overwrite it? (Y/N): '
            answer = raw_input(msg).upper().strip()
            if not answer == 'Y':
                sys.exit('Aborted')
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
            if filename != '.svn']


def find_file(basenames, dir='.'):
    for basename in basenames:
        path = os.path.join(dir, basename)
        if os.path.exists(path):
            return path
    raise IOError('none found in %r: %r' % (dir, basenames))
    
    
def convert_to_correct_type(val):
    """
    Safely evaluate an expression node or a string containing a Python expression. 
    The string or node provided may only consist of the following Python literal 
    structures: strings, numbers, tuples, lists, dicts, booleans, and None.
    """
    import ast
    try:
        val = ast.literal_eval(val)
    except (ValueError, SyntaxError):
        pass
    return val
    
    
def import_python_file(filename):
    filename = os.path.normpath(filename)
    filename = os.path.basename(filename)
    if filename.endswith('.py'):
        module_name = filename[:-3]
    elif filename.endswith('.pyc'):
        module_name = filename[:-4]
    else:
        module_name = filename
        
    try:
        module = __import__(module_name)
        return module
    except ImportError, err:
        logging.error('File "%s" could not be imported: %s' % (filename, err))
        print traceback.format_exc()
        sys.exit(1)
        
        
def run_command(cmd, env=None):
    """
    Runs command cmd and returns the output
    """
    logging.info('Running command "%s"' % cmd)
    if type(cmd) == str:
        cmd = cmd.split()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, env=env)
    output = p.communicate()[0].strip()
    return output
    
                
                
class Properties(ConfigObj):
    def __init__(self, *args, **kwargs):
        kwargs['unrepr'] = True
        ConfigObj.__init__(self, *args, **kwargs)
        
                
                
def updatetree(src, dst, symlinks=False, ignore=None):
    """
    Copies the contents from src onto the tree at dst, overwrites files with the
    same name
    
    Code taken and expanded from python docs
    """
    
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    if not os.path.exists(dst):
        os.makedirs(dst)
        
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                copy2(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error, err:
            errors.extend(err.args[0])
    try:
        copystat(src, dst)
    except WindowsError:
        # can't copy file access times on Windows
        pass
    except OSError, why:
        errors.extend((src, dst, str(why)))
    if errors:
        raise Error(errors)
        
        
def fast_updatetree(src, dst):
    """
    Copies the contents from src onto the tree at dst, overwrites files with the
    same name
    
    Code taken and expanded from python docs
    """
    
    names = os.listdir(src)

    makedirs(dst)
        
    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                copytree(srcname, dstname)
            else:
                copy2(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error, err:
            errors.extend(err.args[0])
    #try:
    #    copystat(src, dst)
    #except WindowsError:
    #    # can't copy file access times on Windows
    #    pass
    #except OSError, why:
    #    errors.extend((src, dst, str(why)))
    if errors:
        raise Error(errors)


def copy(src, dest):
    """
    Copies a file or directory to another file or directory
    """
    if os.path.isfile(src) and os.path.isdir(dest):
        makedirs(dest)
        dest = os.path.join(dest, os.path.basename(src))
        shutil.copy2(src, dest)
    elif os.path.isfile(src):
        makedirs(os.path.dirname(dest))
        shutil.copy2(src, dest)
    elif os.path.isdir(src):
        fast_updatetree(src, dest)
    else:
        logging.error('Cannot copy %s to %s' % (src, dest))
        sys.exit()
    logging.debug('Copied %s to %s' % (src, dest))
        

def csv(string):
    string = string.strip(', ')
    return string.split(',')


class ArgParser(argparse.ArgumentParser):
    def __init__(self, add_log_option=True, *args, **kwargs):
        argparse.ArgumentParser.__init__(self, *args, #add_help=False,
                formatter_class=argparse.ArgumentDefaultsHelpFormatter, **kwargs)

        if add_log_option:
            try:
                self.add_argument('-l', '--log-level', choices=['DEBUG', 'INFO', 'WARNING'],
                                dest='log_level', default='INFO')
            except argparse.ArgumentError:
                # The option may have already been added by a parent
                pass
            
    def parse_known_args(self, *args, **kwargs):
        args, remaining = argparse.ArgumentParser.parse_known_args(self, *args, **kwargs)
        
        global LOG_LEVEL
        # Set log level only once (May have already been deleted from sys.argv)
        if getattr(args, 'log_level', None) and not LOG_LEVEL:
            # Python adds a default handler if some log is generated before here
            # Remove all handlers that have been added automatically
            root_logger = logging.getLogger('')
            for handler in root_logger.handlers:
                root_logger.removeHandler(handler)
            
            LOG_LEVEL = getattr(logging, args.log_level.upper())
            logging.basicConfig(level=LOG_LEVEL, format='%(asctime)-s %(levelname)-8s %(message)s',)
        
        return (args, remaining)
                
    def set_help_active(self):
        self.add_argument(
                '-h', '--help', action='help', default=argparse.SUPPRESS,
                help=('show this help message and exit'))
      
    def directory(self, string):
        if not os.path.isdir(string):
            msg = '%r is not an evaluation directory' % string
            raise argparse.ArgumentTypeError(msg)
        return string
        
        
        
################################################################################
### OrderedDict
################################################################################

class OrderedDict(dict, MutableMapping):
    'Dictionary that remembers insertion order'
    # An inherited dict maps keys to values.
    # The inherited dict provides __getitem__, __len__, __contains__, and get.
    # The remaining methods are order-aware.
    # Big-O running times for all methods are the same as for regular dictionaries.

    # The internal self.__map dictionary maps keys to links in a doubly linked list.
    # The circular doubly linked list starts and ends with a sentinel element.
    # The sentinel element never gets deleted (this simplifies the algorithm).
    # Each link is stored as a list of length three:  [PREV, NEXT, KEY].

    def __init__(self, *args, **kwds):
        '''Initialize an ordered dictionary.  Signature is the same as for
        regular dictionaries, but keyword arguments are not recommended
        because their insertion order is arbitrary.

        '''
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        try:
            self.__root
        except AttributeError:
            self.__root = root = [None, None, None]     # sentinel node
            PREV = 0
            NEXT = 1
            root[PREV] = root[NEXT] = root
            self.__map = {}
        self.update(*args, **kwds)

    def __setitem__(self, key, value, PREV=0, NEXT=1, dict_setitem=dict.__setitem__):
        'od.__setitem__(i, y) <==> od[i]=y'
        # Setting a new item creates a new link which goes at the end of the linked
        # list, and the inherited dictionary is updated with the new key/value pair.
        if key not in self:
            root = self.__root
            last = root[PREV]
            last[NEXT] = root[PREV] = self.__map[key] = [last, root, key]
        dict_setitem(self, key, value)

    def __delitem__(self, key, PREV=0, NEXT=1, dict_delitem=dict.__delitem__):
        'od.__delitem__(y) <==> del od[y]'
        # Deleting an existing item uses self.__map to find the link which is
        # then removed by updating the links in the predecessor and successor nodes.
        dict_delitem(self, key)
        link = self.__map.pop(key)
        link_prev = link[PREV]
        link_next = link[NEXT]
        link_prev[NEXT] = link_next
        link_next[PREV] = link_prev

    def __iter__(self, NEXT=1, KEY=2):
        'od.__iter__() <==> iter(od)'
        # Traverse the linked list in order.
        root = self.__root
        curr = root[NEXT]
        while curr is not root:
            yield curr[KEY]
            curr = curr[NEXT]

    def __reversed__(self, PREV=0, KEY=2):
        'od.__reversed__() <==> reversed(od)'
        # Traverse the linked list in reverse order.
        root = self.__root
        curr = root[PREV]
        while curr is not root:
            yield curr[KEY]
            curr = curr[PREV]

    def __reduce__(self):
        'Return state information for pickling'
        items = [[k, self[k]] for k in self]
        tmp = self.__map, self.__root
        del self.__map, self.__root
        inst_dict = vars(self).copy()
        self.__map, self.__root = tmp
        if inst_dict:
            return (self.__class__, (items,), inst_dict)
        return self.__class__, (items,)

    def clear(self):
        'od.clear() -> None.  Remove all items from od.'
        try:
            for node in self.__map.itervalues():
                del node[:]
            self.__root[:] = [self.__root, self.__root, None]
            self.__map.clear()
        except AttributeError:
            pass
        dict.clear(self)

    setdefault = MutableMapping.setdefault
    update = MutableMapping.update
    pop = MutableMapping.pop
    keys = MutableMapping.keys
    values = MutableMapping.values
    items = MutableMapping.items
    iterkeys = MutableMapping.iterkeys
    itervalues = MutableMapping.itervalues
    iteritems = MutableMapping.iteritems
    __ne__ = MutableMapping.__ne__

    def popitem(self, last=True):
        '''od.popitem() -> (k, v), return and remove a (key, value) pair.
        Pairs are returned in LIFO order if last is true or FIFO order if false.

        '''
        if not self:
            raise KeyError('dictionary is empty')
        key = next(reversed(self) if last else iter(self))
        value = self.pop(key)
        return key, value

    def __repr__(self):
        'od.__repr__() <==> repr(od)'
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, self.items())

    def copy(self):
        'od.copy() -> a shallow copy of od'
        return self.__class__(self)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        '''OD.fromkeys(S[, v]) -> New ordered dictionary with keys from S
        and values equal to v (which defaults to None).

        '''
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def __eq__(self, other):
        '''od.__eq__(y) <==> od==y.  Comparison to another OD is order-sensitive
        while comparison to a regular mapping is order-insensitive.

        '''
        if isinstance(other, OrderedDict):
            return len(self)==len(other) and \
                   all(_imap(_eq, self.iteritems(), other.iteritems()))
        return dict.__eq__(self, other)

    def __del__(self):
        self.clear()                # eliminate cyclical references

