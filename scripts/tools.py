import datetime
import errno
import os
import os.path
from os.path import join as joinpath
import re
import shutil
import subprocess
import sys


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
        path = joinpath(dir, basename)
        if os.path.exists(path):
            return path
    raise IOError("none found in %r: %r" % (dir, basenames))


def make_dir(dirpath, may_exist=False):
    try:
        os.mkdir(dirpath)
    except OSError, e:
        if not (e.errno == errno.EEXIST and may_exist):
            raise


def make_dirs(dirpath):
    for _ in range(10):
        ## HACK! There is a racing condition in os.makedirs in old versions
        ## of Python.
        ## TODO: Replace this with something that works reliably.
        ## (Or just wait for this bug to be fixed -- it probably is by now.)
        try:
            os.makedirs(os.path.abspath(dirpath))
        except OSError, e:
            # Swallow "directory exists already" errors, propagate others.
            if e.errno != errno.EEXIST:
                raise


def copy_files(filenames, dest_dir, src_dir="."):
    make_dirs(dest_dir)
    for filename in filenames:
        shutil.copy(joinpath(src_dir, filename), dest_dir)


def move_files(filenames, dest_dir, src_dir="."):
    make_dirs(dest_dir)
    for filename in filenames:
        shutil.move(joinpath(src_dir, filename), dest_dir)


def delete_files(filenames, dir="."):
    for filename in filenames:
        os.remove(joinpath(dir, filename))


def move_optional_files(filenames, dest_dir, src_dir="."):
    # Returns the files that were actually moved.
    moved = []
    make_dirs(dest_dir)
    for filename in filenames:
        try:
            shutil.move(joinpath(src_dir, filename), dest_dir)
        except IOError, e:
            # Swallow "File not found".
            if e.errno != errno.ENOENT:
                raise
        else:
            moved.append(filename)
    return moved


def make_executable(filename):
    """Make file executable by those who can read it."""
    mode = os.stat(filename).st_mode
    read_mode = mode & 0444
    exec_mode = read_mode >> 2
    os.chmod(filename, mode | exec_mode)


def log(msg, stream=sys.stdout):
    timestamp = datetime.datetime.now().replace(microsecond=0)
    try:
        print >> stream, "[%s] %s" % (timestamp, msg)
        stream.flush()
    except IOError, e:
        # Swallow "Broken pipe" which may appear on Ctrl-C when
        # redirecting stdout.
        if e.errno != errno.EPIPE:
            raise
