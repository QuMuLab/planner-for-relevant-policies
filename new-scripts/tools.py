import os
import sys
import shutil
import subprocess
import re
import traceback
import logging
import contextlib
import time
import math

from external import argparse
from external.configobj import ConfigObj
from external.datasets import DataSet

# Patch configobj's unrepr method. Our version is much faster, but depends on
# Python 2.6.
import external.configobj
from ast import literal_eval as unrepr
external.configobj.unrepr = unrepr


LOG_LEVEL = None

# Directories and files

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPTS_DIR)
DATA_DIR = os.path.join(SCRIPTS_DIR, 'data')
CALLS_DIR = os.path.join(SCRIPTS_DIR, 'calls')
REPORTS_DIR = os.path.join(SCRIPTS_DIR, 'reports')


def setup_logging(level):
    # Python adds a default handler if some log is written before now
    # Remove all handlers that have been added automatically
    root_logger = logging.getLogger('')
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    # Handler which writes LOG_LEVEL messages or higher to stdout
    console = logging.StreamHandler(sys.stdout)
    #console.setLevel(level)
    # set a format which is simpler for console use
    format='%(asctime)-s %(levelname)-8s %(message)s'
    formatter = logging.Formatter(format)
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    root_logger.addHandler(console)
    root_logger.setLevel(level)


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
    return [seq[i:i + size] for i  in range(0, len(seq), size)]


def round_to_next_power_of_ten(i):
    assert i > 0
    return 10**math.ceil(math.log10(i))


def makedirs(dir):
    """
    mkdir variant that does not complain when the dir already exists
    """
    try:
        os.makedirs(dir)
    except OSError:
        # directory probably exists
        pass


def overwrite_dir(dir):
    if os.path.exists(dir):
        if not os.path.exists(os.path.join(dir, 'run')):
            msg = 'The directory "%s" ' % dir
            msg += 'is not empty, do you want to overwrite it? (Y/N): '
            answer = raw_input(msg).upper().strip()
            if not answer == 'Y':
                sys.exit('Aborted')
        shutil.rmtree(dir)
    # We use the os.makedirs method instead of our own here to check if the dir
    # has really been properly deleted.
    os.makedirs(dir)


def remove(filename):
    try:
        os.remove(filename)
    except OSError:
        pass


def natural_sort(alist):
    """Sort alist alphabetically, but special-case numbers to get
    file2.txt before file10.ext."""
    def to_int_if_number(text):
        if text.isdigit():
            return int(text)
        else:
            return text.lower()

    def extract_numbers(text):
        parts = re.split("([0-9]+)", text)
        return map(to_int_if_number, parts)

    return sorted(alist, key=extract_numbers)


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
    Safely evaluate an expression node or a string containing a Python
    expression.
    The string or node provided may only consist of the following Python
    literal structures: strings, numbers, tuples, lists, dicts, booleans
    and None.

    Unused for now.
    """
    import ast
    try:
        out_val = ast.literal_eval(str(val))
        logging.debug('Converted value %s to %s' % (repr(val), repr(out_val)))
        return out_val
    except (ValueError, SyntaxError):
        pass
    #logging.debug('Could not convert value %s' % repr(val))
    return val


def import_python_file(filename):
    parent_dir =  os.path.dirname(filename)
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
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
        ConfigObj.__init__(self, *args, interpolation=False, **kwargs)

    def get_dataset(self):
        data = DataSet()
        for run_id, run in sorted(self.items()):
            run['id-string'] = run_id
            data.append(**run)
        return data


def fast_updatetree(src, dst):
    """
    Copies the contents from src onto the tree at dst, overwrites files with
    the same name

    Code taken and expanded from python docs
    """
    names = os.listdir(src)

    makedirs(dst)

    errors = []
    for name in names:
        # Skip over svn directories
        if name.startswith('.svn'):
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                fast_updatetree(srcname, dstname)
            else:
                shutil.copy2(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Exception, err:
            errors.append(err.args[0])
    if errors:
        raise Exception(errors)


def copy(src, dest, required=True):
    """
    Copies a file or directory to another file or directory
    """
    if os.path.isfile(src) and os.path.isdir(dest):
        makedirs(dest)
        dest = os.path.join(dest, os.path.basename(src))
        func = shutil.copy2
    elif os.path.isfile(src):
        makedirs(os.path.dirname(dest))
        func = shutil.copy2
    elif os.path.isdir(src):
        func = fast_updatetree
    elif required:
        logging.error('Required path %s cannot be copied to %s' % (src, dest))
        sys.exit(1)
    else:
        msg = 'Optional path %s cannot be copied to %s'
        logging.warning(msg % (src, dest))
        return
    try:
        func(src, dest)
    except IOError, err:
        logging.error('Error: The file "%s" could not be copied to "%s": %s' %
                      (src, dest, err))
        if required:
            sys.exit(1)


def csv(string):
    string = string.strip(', ')
    return string.split(',')


class RawDescriptionAndArgumentDefaultsHelpFormatter(argparse.HelpFormatter):
    """
    Help message formatter which retains any formatting in descriptions and adds
    default values to argument help.
    """
    def _fill_text(self, text, width, indent):
        return ''.join([indent + line for line in text.splitlines(True)])

    def _get_help_string(self, action):
        help = action.help
        if '%(default)' not in action.help:
            if action.default is not argparse.SUPPRESS:
                defaulting_nargs = [argparse.OPTIONAL, argparse.ZERO_OR_MORE]
                if action.option_strings or action.nargs in defaulting_nargs:
                    help += ' (default: %(default)s)'
        return help

    def _format_args(self, action, default_metavar):
        """
        We want to show "[environment-specific options]" instead of "...".
        """
        get_metavar = self._metavar_formatter(action, default_metavar)
        if action.nargs == argparse.PARSER:
            return '%s [environment-specific options]' % get_metavar(1)
        else:
            return argparse.HelpFormatter._format_args(self, action, default_metavar)


class ArgParser(argparse.ArgumentParser):
    def __init__(self, add_log_option=True, *args, **kwargs):
        argparse.ArgumentParser.__init__(self, *args, formatter_class=
                                RawDescriptionAndArgumentDefaultsHelpFormatter,
                                         **kwargs)
        if add_log_option:
            try:
                self.add_argument('-l', '--log-level', dest='log_level',
                        choices=['DEBUG', 'INFO', 'WARNING'], default='INFO')
            except argparse.ArgumentError:
                # The option may have already been added by a parent
                pass

    def parse_known_args(self, *args, **kwargs):
        args, remaining = argparse.ArgumentParser.parse_known_args(self, *args,
                                                                   **kwargs)

        global LOG_LEVEL
        # Set log level only once (May have already been deleted from sys.argv)
        if getattr(args, 'log_level', None) and not LOG_LEVEL:
            LOG_LEVEL = getattr(logging, args.log_level.upper())
            setup_logging(LOG_LEVEL)

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


# Parse the log-level and set it
ArgParser().parse_known_args()


class Timer(object):
    def __init__(self):
        self.start_time = time.time()
        self.start_clock = self._clock()

    def _clock(self):
        times = os.times()
        return times[0] + times[1]

    def __str__(self):
        return "[%.3fs CPU, %.3fs wall-clock]" % (
            self._clock() - self.start_clock,
            time.time() - self.start_time)


@contextlib.contextmanager
def timing(text):
    timer = Timer()
    logging.info("%s..." % text)
    sys.stdout.flush()
    yield
    logging.info("%s: %s" % (text, timer))
    sys.stdout.flush()
