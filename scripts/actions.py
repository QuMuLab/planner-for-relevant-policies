from os.path import join as joinpath, splitext

import benchmark
from paths import SRC_DIR
import paths
from tools import (copy_files, move_files, move_optional_files,
                   delete_files, make_dir, make_dirs, make_executable)
import planner_configurations
import os.path


TRANSLATE_OUTPUTS = ["output.sas", "test.groups", "all.groups"]
PREPROCESS_OUTPUTS = ["output"]

def translate_dir(prob):
    return joinpath(paths.RESULTS_DIR, "translate", prob.domain, prob.problem)

def preprocess_dir(prob):
    return joinpath(paths.RESULTS_DIR, "preprocess", prob.domain, prob.problem)

def search_dir(prob, config_name):
    return joinpath(paths.RESULTS_DIR, "search", "version-%s" % config_name,
                    prob.domain, prob.problem)

def translator_executable(relaxed=False):
    basedir = joinpath(SRC_DIR, "translate")
    if relaxed:
        return joinpath(basedir, "translate-relaxed.py")
    else:
        return joinpath(basedir, "translate.py")
    
def preprocessor_executable():
    return joinpath(SRC_DIR, "preprocess", "preprocess")
    
def planner_executable():
    return joinpath(SRC_DIR, "search", "src")

def planner_debug_executable():
    return joinpath(SRC_DIR, "search", "src-debug")


def do_translate(problem, generate_relaxed_problem=False):
    executable = translator_executable(relaxed=generate_relaxed_problem)
    benchmark.run(
        cmd=[executable, problem.domain_file(), problem.problem_file()],
        status="status.log",
        stdout="translate.log",
        stderr="translate.err",
        )
    outdir = translate_dir(problem)
    move_files(["translate.log", "status.log"], outdir)
    if move_optional_files(["translate.err"], outdir):
        # There was an error.
        return False
    else:
        move_files(TRANSLATE_OUTPUTS, outdir)
        return True
    

def do_preprocess(problem):
    copy_files(TRANSLATE_OUTPUTS, ".", src_dir=translate_dir(problem))
    executable = preprocessor_executable()
    benchmark.run(
        cmd=[executable],
        status="status.log",
        stdin="output.sas",
        stdout="preprocess.log",
        stderr="preprocess.err",
        )
    outdir = preprocess_dir(problem)
    move_files(["preprocess.log", "status.log"], outdir)
    delete_files(TRANSLATE_OUTPUTS)
    if move_optional_files(["preprocess.err"], outdir):
        # There was an error.
        return False
    else:
        move_files(PREPROCESS_OUTPUTS, outdir)
        return True


def do_search(problem, configname, timeout, memory, debug=False):
    # TODO: Currently, do_search returns an error msg on error and
    #       None on no error, while do_translate/do_preprocess return
    #       True/False for success/no success. This should be unified.
    #       Maybe throw exceptions if something goes wrong? Also,
    #       maybe we should allow for warnings in addition to errors.
    #       The "skipped -- dir exists" stuff should maybe just be a
    #       warning.
    outdir = search_dir(problem, configname)
    if not debug:
        if os.path.exists(outdir):
            return "skipped [%s] %s -- dir exists" % (configname, problem)
        elif not os.path.exists(translate_dir(problem)):
            return "Translated files for %s not available." % problem
        elif not os.path.exists(preprocess_dir(problem)):
            return "Preprocessed files for %s not available." % problem
    if debug and not os.path.exists(translate_dir(problem)):
        # Do not abort if translation does not exist. Don't store search output.
        # (Instead, translate if necessary and always search.)
        print "Translating and Preprocessing..."
        success = do_translate(problem)
        if not success:
            return "Translating %s failed." % problem
        success = do_preprocess(problem)
        if not success:
            return "Preprocessing %s failed." % problem
    copy_files(TRANSLATE_OUTPUTS, ".", src_dir=translate_dir(problem))
    copy_files(PREPROCESS_OUTPUTS, ".", src_dir=preprocess_dir(problem))
    if debug: # Write planner output to screen instead of file.
        planner = planner_debug_executable()
        success = benchmark.run(
            cmd=[planner]+planner_configurations.get_config(configname),
            timeout=timeout,
            memory=memory,
            status="status.log",
            stdin="output",
            )
        if success:
            delete_files(["sas_plan"])
            delete_files(["status.log"])
    else:
        planner = planner_executable()
        success = benchmark.run(
            cmd=[planner]+planner_configurations.get_config(configname),
            timeout=timeout,
            memory=memory,
            status="status.log",
            stdin="output",
            stdout="search.log",
            stderr="search.err",
            )
        if success:
            move_files(["sas_plan"], outdir)
        move_files(["search.log", "status.log"], outdir)
        move_optional_files(["search.err"], outdir)
    delete_files(PREPROCESS_OUTPUTS)
    delete_files(TRANSLATE_OUTPUTS)
    return None


def prepare_gkigrid_job_search(jobfile, problems, configs, timeout, memory):
    num_tasks = len(problems) * len(configs)
    jobfile_base = splitext(jobfile)[0]

    driver_params = {
        "logfile": jobfile_base + ".log",
        "errfile": jobfile_base + ".err",
        "driver_timeout": timeout + 30,
        "num_tasks": num_tasks,
        }
    header = open("data/gkigrid-job-header.q").read() % driver_params

    task_template = open("data/gkigrid-task").read().rstrip("\n") + "\n"

    jobfile_parts = [header.rstrip("\n") + "\n"]

    task_num = 1
    for problem in problems:
        for config_name, config in configs:
            ## TODO: This way of quoting is not perfect and should be fixed,
            ##       but it will work for now.
            config = " ".join("'%s'" % arg for arg in config)

            ## TODO: Should we put the automagic parameter selection back in?
            ## "logistics00": "200000",
            ## "pipesworld-notankage": "2500",
            ## "pipesworld-tankage": "1000",
            ## "psr-small": "200000",
            ## "satellite": "10000A3",
            ## "tpp": "50000A3",
            result_dir = search_dir(problem, config_name)
            task_params = {
                "task_num": task_num,
                "timeout": timeout,
                "memory_kb": memory * 1024,
                "result_dir": result_dir,
                "planner_executable": planner_executable(),
                "config_name": config_name,
                "config": config,
                "preprocessed_input": joinpath(preprocess_dir(problem), "output"),
                "mutex_file": joinpath(translate_dir(problem), "all.groups"),
                }
            task = task_template % task_params
            jobfile_parts.append(task)
            task_num += 1

    open(jobfile, "w").write("".join(jobfile_parts))
    make_executable(jobfile)


def prepare_gkigrid_job_preprocess(jobfile, problems, timeout):
    num_tasks = len(problems)
    jobfile_base = splitext(jobfile)[0]

    driver_params = {
        "logfile": jobfile_base + ".log",
        "errfile": jobfile_base + ".err",
        "driver_timeout": 2 * timeout + 30,
        "num_tasks": num_tasks,
        }

    header_template = open("data/gkigrid-preprocess-job-header.q").read()
    header = (header_template % driver_params).rstrip("\n") + "\n"

    task_template = open("data/gkigrid-preprocess-task").read()
    task_template = task_template.rstrip("\n") + "\n"

    jobfile_parts = [header]

    task_num = 1
    for problem in problems:
        trans_result_dir = translate_dir(problem)
        pre_result_dir = preprocess_dir(problem)
        task_params = {
            "task_num": task_num,
            "pddl_domain": problem.domain_file(),
            "pddl_problem": problem.problem_file(),
            "translator_executable": translator_executable(),
            "translator_timeout": timeout,
            "translate_dir": translate_dir(problem),
            "preprocessor_executable": preprocessor_executable(),
            "preprocessor_timeout": timeout,
            "preprocess_dir": preprocess_dir(problem),
            }
        task = task_template % task_params
        jobfile_parts.append(task)
        task_num += 1

    open(jobfile, "w").write("".join(jobfile_parts))
    make_executable(jobfile)


class Result(object):
    length = None
    expanded = None
    generated = None
    search_time = None
    total_time = None
    completely_explored = False
    status = "???"
    def __init__(self, problem, arguments, solved, present, complete, **kwargs):
        self.problem = problem
        self.arguments = arguments
        self.solved = solved
        self.present = present
        self.complete = complete
        self.__dict__.update(kwargs)
        ## Commented out the folloing assertion because it fails e.g.
        ## for Mystery07, where the initial state is a dead end. Total
        ## time is not reported in this case, and hence self.complete
        ## is false. TODO: Also output total_time in this case.
        # assert self.complete == (self.length is not None or self.completely_explored)
        assert (self.length is not None) == (self.status == "OK"), self
        assert (self.completely_explored) == (self.status == "failure"), self

    def __repr__(self):
        data = sorted(self.__dict__.items())
        return "<Result %#x: %s>" % (
            id(self), ", ".join("%s: %r" % entry for entry in data))

def parse_result(problem, arguments, cutoff_time=None):
    current_file = [None]
    current_line = [None]
    def verify(condition, *extra_info):
        if extra_info:
            extra_text = " %s" % (extra_info,)
        else:
            extra_text = ""
        assert condition, "[%s:%s]%s" % (
            current_file[0], current_line[0], extra_text)
    def read_lines(filename):
        path = joinpath(search_dir(problem, arguments), filename)
        current_file[0] = path
        try:
            for line in open(path):
                current_line[0] = line.strip()
                yield current_line[0]
        except IOError:
            pass

    data = {}
    data["present"] = False
    for line in read_lines("search.log"):
        data["present"] = True
        if "until last jump" in line:
            continue
        parts = line.split()
        if not parts:
            continue
        if parts[:2] == ["Plan", "length:"]:
            verify(parts[3:] == ["step(s)."])
            data["length"] = int(parts[2])
        elif parts[:2] == ["f", "="] and "init_h" not in data:
            data["init_h"] = int(parts[2])
        elif parts[:4] == ["Initial", "state", "h", "value"]:
            assert data["init_h"] == int(parts[4].rstrip("."))
        elif line == "Completely explored state space -- no solution!":
            data["completely_explored"] = True
        elif parts[0] == "Expanded":
            verify(parts[2:] == ["state(s)."])
            data["expanded"] = int(parts[1])
        elif parts[0] == "Generated":
            verify(parts[2:] == ["state(s)."])
            data["generated"] = int(parts[1])
        elif parts[:2] == ["Search", "time:"]:
            verify(len(parts) == 3 and parts[2].endswith("s"))
            data["search_time"] = float(parts[2][:-1])
        elif parts[:2] == ["Total", "time:"]:
            verify(len(parts) == 3 and parts[2].endswith("s"))
            data["total_time"] = float(parts[2][:-1])

    for line in read_lines("search.err"):
        if "does not support" in line:
            data["status"] = "unsupported"

    ## HACK HACK HACK -- cluster generates no status.log.
    if "length" in data:
        data["status"] = "OK"
    elif "completely_explored" in data:
        data["status"] = "failure"
    else:
        data["status"] = "NOT OK"

    for line in read_lines("status.log"):
        parts = line.split()
        if parts[0] == "timeout:" and parts[1] != "none":
            verify(parts[2:] == ["seconds"])
            timeout = float(parts[1])
        elif parts[:3] == ["CPU", "time", "passed:"]:
            verify(parts[4:] == ["seconds"])
            cpu_time = float(parts[3])
        elif parts[:2] == ["return", "code:"]:
            if parts[2:] == ["0", "[success]"]:
                data["status"] = "OK"
            elif parts[2:] == ["1", "[failure]"]:
                if data.get("status") != "unsupported":
                    data["status"] = "failure"
            elif parts[2:] == ["-9", "[SIGKILL]"]:
                verify(cpu_time + 0.1 >= timeout, cpu_time, timeout)
                data["status"] = "TIMEOUT"
            elif parts[2:] == ["-6", "[SIGABRT]"]:
                err_lines = list(read_lines("search.err"))
                verify(err_lines == [
                    "terminate called after throwing an instance of "
                    "'std::bad_alloc'", "what():  St9bad_alloc"] or
                       err_lines == [
                    "terminate called after throwing an instance of "
                    "'St9bad_alloc'", "what():  St9bad_alloc"],
                       err_lines)
                data["status"] = "MEMORY"
            elif parts[2:] == ["-11", "[SIGSEGV]"]:
                # Remove attributes that suggest this one is done.
                data.pop("completely_explored", None)
                data.pop("search_time", None)
                data.pop("total_time", None)
                data["status"] = "***SEGFAULT***"
            else:
                verify(False)

    solved = (("length" in data) and
              (cutoff_time is None or data["search_time"] < cutoff_time))
    return Result(problem=problem, arguments=arguments, solved=solved,
                  complete="total_time" in data,
                  **data)
