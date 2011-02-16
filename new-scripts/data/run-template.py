#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import resource
import sys
import time
import subprocess
import glob
import datetime
import signal


***ENVIRONMENT_VARIABLES***

timeout = ***TIMEOUT***
memory = ***MEMORY***       # Memory in MiB
memory *= 1024 * 1024       # Memory in Bytes


KILL_DELAY = 5               # how long we wait between SIGTERM and SIGKILL
CHECK_INTERVAL = 0.5           # how often we query the process group status

# make sure we're in the run directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

redirects = {'stdout': open('run.log', 'a'), 'stderr': open('run.err', 'a')}
properties_file = open('properties', 'a')


#------------------------------------------------------------------------------

JIFFIES_PER_SECOND = 100


class Process(object):
    def __init__(self, pid):
        stat = open("/proc/%d/stat" % pid).read()
        cmdline = open("/proc/%d/cmdline" % pid).read()

        # Don't use stat.split(): the command can contain spaces.
        # Be careful which "()" to match: the command name can contain
        # parentheses.
        prefix, lparen, rest = stat.partition("(")
        command, rparen, suffix = rest.rpartition(")")
        parts = suffix.split()

        self.pid = pid
        self.ppid = int(parts[1])
        self.pgrp = int(parts[2])
        self.utime = int(parts[11])
        self.stime = int(parts[12])
        self.cutime = int(parts[13])
        self.cstime = int(parts[14])
        self.vsize = int(parts[20])
        self.cmdline = cmdline.rstrip("\0\n").replace("\0", " ")

    def total_time(self):
        return self.utime + self.stime + self.cutime + self.cstime


def read_processes():
    for filename in os.listdir("/proc"):
        if filename.isdigit():
            pid = int(filename)
            # Be careful about a race conditions here: The process
            # may have disappeared after the os.listdir call.
            try:
                yield Process(pid)
            except EnvironmentError:
                pass


class ProcessGroup(object):
    def __init__(self, pgrp):
        self.processes = [process for process in read_processes()
                          if process.pgrp == pgrp]

    def __nonzero__(self):
        return bool(self.processes)

    def pids(self):
        return [p.pid for p in self.processes]

    def total_time(self):
        # Cumulated time for this process group, in seconds
        total_jiffies = sum([p.total_time() for p in self.processes])
        return total_jiffies / float(JIFFIES_PER_SECOND)

    def total_vsize(self):
        # Cumulated virtual memory for this process group, in MB
        total_bytes = sum([p.vsize for p in self.processes])
        return total_bytes / float(2 ** 20)

#------------------------------------------------------------------------------

class KilledError(Exception):
    def __init__(self, signal):
        self.signal = signal
    def __str__(self):
        return repr('process killed with signal %s' % self.signal)

def kill_pgrp(pgrp, sig):
    try:
        os.killpg(pgrp, sig)
    except OSError:
        #TODO: log error somewhere
        pass
    else:
        raise KilledError(sig)

def watch(child_pid):
    term_attempted = False
    real_time = 0
    while True:
        time.sleep(CHECK_INTERVAL)
        real_time += CHECK_INTERVAL

        group = ProcessGroup(child_pid)
        ## Generate the children information before the waitpid call to
        ## avoid a race condition. This way, we know that the child_pid
        ## is a descendant.

        pid, exit_status = os.waitpid(child_pid, os.WNOHANG)
        if (pid, exit_status) != (0, 0):
            print 'process terminated', pid, exit_status
            for func in [os.WIFSTOPPED, os.WIFSIGNALED, os.WSTOPSIG,
                         os.WTERMSIG]:
                print func.__name__, func(exit_status)
            break

        total_time = group.total_time()
        total_vsize = group.total_vsize()
        print "[real-time %d] total_time: %.2f" % (real_time, total_time)
        print "[real-time %d] total_vsize: %.2f" % (real_time, total_vsize)

        try_term = (total_time >= timeout or
                    real_time >= 1.5 * timeout or
                    total_vsize > memory)
        try_kill = (total_time >= timeout + KILL_DELAY or
                    real_time >= 1.5 * timeout + KILL_DELAY or
                    total_vsize > 1.5 * memory)

        if try_term and not term_attempted:
            print "aborting children with SIGTERM..."
            print "children found: %s" % group.pids()
            kill_pgrp(child_pid, signal.SIGTERM)
            term_attempted = True
        elif term_attempted and try_kill:
            print "aborting children with SIGKILL..."
            print "children found: %s" % group.pids()
            kill_pgrp(child_pid, signal.SIGKILL)

    # Even if we got here, there may be orphaned children or something
    # we may have missed due to a race condition. Check for that and kill.

    group = ProcessGroup(child_pid)
    if group:
        # If we have reason to suspect someone still lives, first try to
        # kill them nicely and wait a bit.
        print "aborting orphaned children with SIGTERM..."
        print "children found: %s" % group.pids()
        kill_pgrp(child_pid, signal.SIGTERM)
        time.sleep(1)

    # Either way, kill properly for good measure. Note that it's not clear
    # if checking the ProcessGroup for emptiness is reliable, because
    # reading the process table may not be atomic, so for this last blow,
    # we don't do an emptiness test.
    kill_pgrp(child_pid, signal.SIGKILL)

#------------------------------------------------------------------------------


def set_limit(kind, amount):
    try:
        resource.setrlimit(kind, (amount, amount))
    except (OSError, ValueError), e:
        redirects['stderr'].write('Error: %s\n' % e)
        sys.exit(1)

def prepare_process():
    os.setpgrp()
    set_limit(resource.RLIMIT_CPU, timeout)
    set_limit(resource.RLIMIT_AS, memory)
    set_limit(resource.RLIMIT_CORE, 0)


def add_property(name, value):
    properties_file.write('%s = %s\n' % (name, repr(value)))
    properties_file.flush()

def save_returncode(command_name, value):
    os.environ['%s_RETURNCODE' % command_name.upper()] = str(value)
    add_property('%s_returncode' % command_name.lower(), value)
    # TODO: Do we want to mark errors here already?
    # TODO: Would it be better to save just one "fatal_error" for each run?
    error = 0 if value == 0 else 1
    add_property('%s_error' % command_name.lower(), error)


def run_command(command, name):
    """Calls the command with the subprocess module."""
    # TODO: Handle segmentation faults (bad alloc)
    stderr = redirects['stderr']
    start_times = os.times()
    add_property(name + '_start_time', str(datetime.datetime.now()))

    try:
        process = subprocess.Popen(command, shell=True,
                                   preexec_fn=prepare_process, **redirects)
        watch(process.pid)
        # If no error occured we assume everything went fine
        print 'RETCODE', process.poll()  # poll always returns None after watch
        returncode = 0
    except MemoryError:
        stderr.write('Error: %s MemoryError\n' % name)
        # Use normal error code (1) since a MemoryError is an expected error
        returncode = 1
    except KeyboardInterrupt:
        stderr.write('Error: %s interrupted\n' % name)
        # Set returncode to SIGINT, this is what Ctrl-C generates
        returncode = 2
    except KilledError as err:
        stderr.write('Error: %s killed with signal %s\n' % (name, err.signal))
        returncode = 3  # was 137
    except Exception as err:
        stderr.write('Error: %s "%s"\n' % (name, err))
        # Set returncode to a special value
        returncode = 999

    end_times = os.times()
    time = end_times[2] + end_times[3] - start_times[2] - start_times[3]
    add_property(name + '_time', round(time, 3))

    save_returncode(name, returncode)
    return returncode


command = """***RUN_COMMAND***"""
returncode = run_command(command, 'command')


optional_output = ***OPTIONAL_OUTPUT***
required_output = ***REQUIRED_OUTPUT***
resources = ***RESOURCES***
run_files = ['run', 'run.log', 'run.err', 'properties']

# Check the output files
if returncode == 0:
    found_files = os.listdir('.')

    detected_optional_files = []
    for file_glob in optional_output:
        detected_optional_files.extend(glob.glob(file_glob))

    expected_files = (resources + run_files + detected_optional_files +
                      required_output)

    for file in found_files:
        if file not in expected_files:
            # We have more files than expected
            redirects['stderr'].write('Error: Unexpected file "%s"\n' % file)
    for required_file in required_output:
        if not required_file in found_files:
            # We are missing a required file
            msg = 'Error: Required file missing "%s"\n' % required_file
            redirects['stderr'].write(msg)
