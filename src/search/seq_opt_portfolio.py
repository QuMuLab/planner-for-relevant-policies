# -*- coding: utf-8 -*-

import os
import os.path
import resource
import sys


DEFAULT_TIMEOUT = 1800


def set_ipc_memory_limit():
    # Set limit of 6 GB (the IPC limit) minus 64 MB as a safety buffer
    # for this process and the ones that called it.
    IPC_LIMIT = 6 * 2 ** 30        # 6 GB is the IPC limit
    SAFETY_BUFFER = 64 * 2 ** 20   # 32 MB for this process and its ancestors
    limit = IPC_LIMIT - SAFETY_BUFFER
    try:
        resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    except ValueError:
        print "WARNING! failed to set resource limit"


def run(configs, timeout=DEFAULT_TIMEOUT):
    extra_args = sys.argv[1:]
    assert len(extra_args) == 3, extra_args
    assert extra_args[0][-1] in ["1", "2", "4"], extra_args
    planner = extra_args.pop(0)
    assert extra_args[0] == "--plan-file", extra_args
    plan_file = extra_args[1]

    try:
        os.unlink(plan_file)
    except EnvironmentError:
        pass

    remaining_time_at_start = float(timeout)
    try:
        for line in open("elapsed.time"):
            if line.strip():
                remaining_time_at_start -= float(line)
    except EnvironmentError:
        print "WARNING! elapsed_time not found -- assuming full time available."

    print "remaining time at start: %s" % remaining_time_at_start

    for pos, (relative_time, args) in enumerate(configs):
        remaining_time = remaining_time_at_start - sum(os.times()[:4])
        print "remaining time: %s" % remaining_time
        remaining_relative_time = sum(config[0] for config in configs[pos:])
        print "config %d: relative time %d, remaining %d" % (
            pos, relative_time, remaining_relative_time)
        run_timeout = remaining_time * relative_time / remaining_relative_time
        print "timeout: %.2f" % run_timeout
        complete_args = [planner] + args + extra_args
        print "args: %s" % complete_args
        sys.stdout.flush()
        if not os.fork():
            os.close(0)
            os.open("output", os.O_RDONLY)
            set_ipc_memory_limit()
            if relative_time != remaining_relative_time:
                resource.setrlimit(resource.RLIMIT_CPU, (
                    int(run_timeout), int(run_timeout)))
            os.execl(planner, *complete_args)
        os.wait()
        if os.path.exists(plan_file):
            print "Plan found!"
            break
