from optparse import OptionValueError
import os
from os.path import join as joinpath
import shutil
import socket
import sys
import threading
import Queue

import tools

def get_tempdir_name(id):
    return "tmpdir-%s-%d-%d" % (socket.gethostname(), os.getpid(), id)

def populate_option_parser(parser):
    def check_and_store(dummy1, dummy2, value, parser):
        if value < 1:
            raise OptionValueError("number of processes must be at least 1")
        parser.values.jobs = value
    parser.add_option(
        "-j", "--jobs", dest="jobs", type="int", default=1,
        action="callback", callback=check_and_store,
        help="number of parallel processes to use (default: 1)")
        

def run_jobs(num_processes, jobs, run_job_func):
    num_processes = min(num_processes, len(jobs))
    tools.log("Using %d processes for %d jobs." % (
        num_processes, len(jobs)))

    queue = Queue.Queue()

    errors = []
    critical_errors = []

    class WorkerThread(threading.Thread):
        def __init__(self, thread_id):
            threading.Thread.__init__(self)
            self.thread_id = thread_id

        def log(self, msg):
            tools.log("#%d: %s" % (self.thread_id, msg))

        def run(self):
            thread_had_critical_error = False
            try:
                tmpdir = get_tempdir_name(self.thread_id)
                try:
                    os.mkdir(tmpdir)
                except OSError:
                    pass
                while True:
                    try:
                        job = queue.get_nowait()
                    except Queue.Empty:
                        break
                    if not critical_errors:
                        pid = os.fork()
                        if not pid:
                            # We need to fork because all threads share the same
                            # working directory.
                            os.chdir(tmpdir)
                            error = run_job_func(job, self.log)
                            if error:
                                open("errmsg", "w").write(error)
                            raise SystemExit
                        os.waitpid(pid, 0)

                        if os.listdir(tmpdir) == ["errmsg"]:
                            error = open(joinpath(tmpdir, "errmsg")).read()
                            self.log(error)
                            errors.append(error)
                            tools.delete_files(["errmsg"], tmpdir)
                        if os.listdir(tmpdir):
                            msg = "temp dir %s not empty" % tmpdir
                            critical_errors.append(msg)
                            thread_had_critical_error = True
                    queue.task_done()
                if not thread_had_critical_error:
                    shutil.rmtree(tmpdir, True)
                    self.log("ran out of work")
            except KeyboardInterrupt:
                pass

    for job in jobs:
        queue.put(job)
    threads = []
    for thread_id in range(num_processes):
        thread = WorkerThread(thread_id)
        thread.start()
        threads.append(thread)
    try:
        queue.join()
    except KeyboardInterrupt, e:
        tools.log("Interrupted!")
        raise SystemExit(1)

    # Let threads finish after queue is done, so that their final
    # output is shown before our final output.
    for thread in threads:
        thread.join()

    # Policy: critical errors are errors *of this script*. They are
    # sent to stderr and cause immediate termination. Currently
    # running jobs may finish, but no new jobs are started.
    #
    # "Regular" errors are failures of the invoked program that
    # indicate bugs (e.g. translator failures) of those programs. Such
    # errors are printed to stdout and do not cause early termination
    # of this script.
    if critical_errors:
        tools.log("There were critical errors. See details on stderr.")
        for msg in critical_errors:
            tools.log("critical error: %s" % msg, stream=sys.stderr)
        raise SystemExit(1)

    if errors:
        tools.log("There were errors.")
        for msg in errors:
            tools.log("error: %s" % msg)
