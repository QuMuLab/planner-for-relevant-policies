from optparse import OptionValueError
import os
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

    class WorkerThread(threading.Thread):
        def __init__(self, thread_id):
            threading.Thread.__init__(self)
            self.thread_id = thread_id

        def log(self, msg):
            tools.log("#%d: %s" % (self.thread_id, msg))

        def run(self):
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
                    pid = os.fork()
                    if not pid:
                        # We need to fork because all threads share the same
                        # working directory.
                        os.chdir(tmpdir)
                        run_job_func(job, self.log)
                        raise SystemExit
                    os.waitpid(pid, 0)
                    queue.task_done()
                shutil.rmtree(tmpdir, True)
                self.log("ran out of work")
            except KeyboardInterrupt:
                pass

    for job in jobs:
        queue.put(job) 
    for thread_id in range(num_processes):
        WorkerThread(thread_id).start()
    try:
        queue.join()
    except KeyboardInterrupt, e:
        tools.log("Interrupted!")
        raise SystemExit(1)

