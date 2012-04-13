import datetime
import os
import resource
import signal
import socket
import subprocess


def run(cmd, timeout=None, memory=None, status="/dev/null",
        stdin=None, stdout=None, stderr=None):
    pid = os.fork()
    if not pid:
        log = open(status, "w")
        print >> log, "command: %s" % cmd

        print >> log, "host: %s" % socket.gethostname()

        wallclock_before = datetime.datetime.now()
        print >> log, "started at: %s" % wallclock_before

        if timeout:
            print >> log, "timeout: %d seconds" % timeout
            resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout))
        else:
            print >> log, "timeout: none"

        if memory:
            print >> log, "memory limit: %d MB" % memory
            bytes = memory * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (bytes, bytes))
        else:
            print >> log, "memory limit: none"
        log.flush()

        redirections = {}
        if stdin:
            redirections["stdin"] = open(stdin, "r")
        if stdout:
            redirections["stdout"] = open(stdout, "w")
        if stderr:
            redirections["stderr"] = open(stderr, "w")

        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        times_before = os.times()[2] + os.times()[3]
        retcode = subprocess.call(cmd, **redirections)
        times_after = os.times()[2] + os.times()[3]
        wallclock_after = datetime.datetime.now()

        print >> log, "finished at: %s" % wallclock_after
        print >> log, "wall-clock time passed: %s" % (
            wallclock_after - wallclock_before)
        print >> log, "CPU time passed: %s seconds" % (
            times_after - times_before)
        print >> log, "return code: %d [%s]" % (
            retcode, interpret_returncode(retcode))

        if stderr:
            if os.stat(stderr).st_size == 0:
                os.unlink(stderr)
                print >> log, "There was no stderr output."
            else:
                print >> log, "There was stderr output. See %s." % stderr
        else:
            print >> log, "Warning: stderr was not captured."
        log.close()

        # Return sucess (0) or failure (1) based on retcode.
        os._exit(int(bool(retcode)))

    status = os.waitpid(pid, 0)[1]
    assert status in [0, 256], status
    return status == 0


def interpret_returncode(retcode):
    if retcode == 0:
        return "success"
    elif retcode < 0:
        return get_signal_name(-retcode)
    else:
        return "failure"


def get_signal_name(sig):
    names_to_signals = dict((number, name)
                            for (name, number) in signal.__dict__.items()
                            if name.startswith("SIG"))
    return names_to_signals.get(sig, "unknown signal")
