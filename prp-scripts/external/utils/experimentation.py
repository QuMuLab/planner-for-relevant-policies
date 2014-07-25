###########################################
# General utils running experiments
######################################

import sys, re, os, resource

# Degrade gracefully when using python < 2.6
try:
    from itertools import product
except:
    def product(*args, **kwds):
        # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
        # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
        pools = map(tuple, args) * kwds.get('repeat', 1)
        result = [[]]
        for pool in pools:
            result = [x+[y] for x in result for y in pool]
        for prod in result:
            yield tuple(prod)


from result_handlers import Result, ResultSet

def check_memout(result):
    MEMORY_CODES = ['std::bad_alloc', 'MemoryError', 'NO MEMORY']
    for f in [result.output_file, result.error_file]:
        for code in MEMORY_CODES:
            if match_value(f, code):
                return True
    return False

def get_value(file_name, regex, value_type = float):
    """ Lifts a value from a file based on a regex passed in. """

    # Get the file
    f = open(file_name, 'r')
    file_text = "\n".join(f.readlines())
    f.close()

    # Get the text of the time
    pattern = re.compile(regex, re.MULTILINE)
    results = pattern.search(file_text)
    if results:
        return value_type(results.group(1))
    else:
        print "Could not find the value, %s, in the file provided: %s" % (regex, file_name)
        return value_type(0.0)

def match_value(file_name, regex):
    """ Checks if the regex matches the contents of a specified file. """

    # Get the file
    f = open(file_name, 'r')
    file_text = "\n".join(f.readlines())
    f.close()

    # Get the text of the time
    pattern = re.compile(regex, re.MULTILINE)
    if pattern.search(file_text):
        return True
    else:
        return False

def get_lines(file_name, lower_bound = None, upper_bound = None):
    """ Gets all of the lines between the regex lower bound and upper bound. """

    toReturn = []

    # Get the file
    f = open(file_name, 'r')
    file_lines = [line.rstrip("\n") for line in f.readlines()]
    f.close()

    if not lower_bound:
        accepting = True
    else:
        accepting = False
        pattern_low = re.compile(lower_bound, re.MULTILINE)

    if not upper_bound:
        upper_bound = 'THIS IS SOME CRAZY STRING THAT NOONE SHOULD EVER HAVE -- NARF!'

    pattern_high = re.compile(upper_bound, re.MULTILINE)

    for line in file_lines:
        if accepting:
            if pattern_high.search(line):
                return toReturn

            toReturn.append(line)
        else:
            if pattern_low.search(line):
                accepting = True

    return toReturn

def run_command(command_string, output_file = 'OUT', error_file = None, MEMLIMIT = -1, TIMELIMIT = -1):
    out_file_func = lambda x: output_file
    err_file_func = None
    
    if error_file:
        err_file_func = lambda x: error_file
    
    results = run_experiment( base_command = command_string,
                              time_limit = TIMELIMIT,
                              memory_limit = MEMLIMIT,
                              output_file_func = out_file_func,
                              error_file_func = err_file_func )
    
    return results[results.get_ids()[0]]

def run_experiment( base_directory = ".",
                    base_command = None,
                    single_arguments = None,
                    parameters = None,
                    time_limit = -1,
                    memory_limit = -1,
                    results_dir = None,
                    progress_file = '/dev/null',
                    processors = 1,
                    sandbox = None,
                    trials = 1,
                    output_file_func = (lambda res: res.id),
                    error_file_func = None,
                    clean_sandbox = False
                    ):

    if not base_command:
        print "Must supply command for the experiment."
        return

    #--- Make sure the default settings are appropriate
    single_arguments = single_arguments or []
    parameters = parameters or {}
    
    if results_dir:
        results_dir = os.path.abspath(results_dir)
        if not os.path.isdir(results_dir):
            os.mkdir(results_dir)
    else:
        results_dir = '.'
    
    if progress_file:
        progress_file = os.path.abspath(progress_file)
    base_directory = os.path.abspath(base_directory)

    #--- Change to the proper directory
    cur_dir = os.path.abspath(os.curdir)
    os.chdir(base_directory)

    #--- Build the commands to be run
    param_list = []
    single_arg_list = []

    #- Format the single arguments as fake parameters
    if single_arguments:
        for item in single_arguments.keys():
            single_list = []
            for setting in single_arguments[item]:
                single_list.append("%sKRDELIMNARF%s" % (item, setting))

            single_arg_list.append(single_list)

    #- Format the parameters as arguments
    if parameters:
        for item in parameters.keys():
            single_list = []
            for setting in parameters[item]:
                single_list.append("%s %s" % (item, setting))

            param_list.append(single_list)

    results = ResultSet()
    run_num = 0

    for single_arg_settings in product(*single_arg_list):

        single_arg_settings_string = " ".join(
            [item.split("KRDELIMNARF")[1] for item in \
             filter(lambda x: len(x.split("KRDELIMNARF")) > 1, single_arg_settings)
             ])

        for parameter_settings in product(*param_list):
            parameter_settings_string = " ".join(parameter_settings)
            
            for i in range(trials):
                
                # Create the Result object first so we can create the output file
                res = Result(run_num, single_arg_settings, parameter_settings)
                res.trial = i

                output_file = "%s/%s" % (results_dir, str(output_file_func(res)))
                if error_file_func:
                    error_file = "%s/%s" % (results_dir, str(error_file_func(res)))
                else:
                    error_file = "%s/%s.err" % (results_dir, str(output_file_func(res)))
                
                res.output_file = output_file
                res.error_file = error_file
    
                script_command = base_command
                if '' != single_arg_settings_string:
                    script_command += " " + single_arg_settings_string
                if '' != parameter_settings_string:
                    script_command += " " + parameter_settings_string
                script_command += " > %s 2>%s" % (output_file, error_file)
                
                res.command = script_command

                results.add_result(run_num, res)
    
                run_num += 1

    _run_multiple(results, time_limit, memory_limit, processors, progress_file, sandbox, clean_sandbox)

    if sandbox and not clean_sandbox:
        os.system("mv *-sandbox-%s %s" % (sandbox, results_dir))

    #--- Change back to the proper directory
    os.chdir(cur_dir)

    return results


def _timeout_command(cmd, timeout):
    """call shell-command and either return its output or kill it
    if it doesn't normally exit within timeout seconds and return None"""
    import subprocess, datetime, time, signal

    start = datetime.datetime.now()
    #process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process = subprocess.Popen(cmd, shell=True)

    while process.poll() is None:
        time.sleep(1)
        now = datetime.datetime.now()
        if (now - start).seconds > timeout:
            os.kill(process.pid, signal.SIGKILL)
            os.waitpid(process.pid, os.WNOHANG)
            return 0

    return process.returncode


def _run_multiple(cmds, timeout, memory, cores, progress_file, sandbox, clean_sandbox):
        #--- Convert the memory
    memory *= 1024 * 1024

    #--- Build the untried stack and processor array
    todo = cmds.get_ids()
    pids = {}
    times = {}

    #--- Deal with the progress monitoring
    max = float(len(todo))
    last = 0.

    #--- Solve all of the problems
    while len(todo) > 0:
        #-- Deal with the progress monitoring
        remaining = 1 - (float(len(todo)) / max)
        if remaining > last:
            message = "%d%% complete" % int(100 * remaining)
            last += 0.05

            if progress_file:
                os.system("echo \"%s\" > %s" % (message, progress_file))
            else:
                print message

        #-- Get the problem id
        id = todo.pop()

        #-- If all the cores are taken, hold off until one frees up
        if len(pids.keys()) == cores:
            (pid, status) = os.wait()
            
            exit_code = status >> 8
            signal_num = status % 256
            
            time_passed = os.times()[-1] - times.pop(pid)
            old_id = pids.pop(pid)

            cmds[old_id].runtime = time_passed
            cmds[old_id].timed_out = (time_passed >= timeout) and (timeout > 0)
            cmds[old_id].return_code = exit_code
            cmds[old_id].mem_out = (time_passed < timeout) and check_memout(cmds[old_id])

        #-- Fire up the new process
        pid = os.fork()

        if pid:
            pids[pid] = id
            times[pid] = os.times()[-1]
        else:
                
            if memory > 0:
                resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

            if sandbox:
                os.system("mkdir %d-sandbox-%s" % (cmds[id].id, sandbox))
                os.chdir("%d-sandbox-%s" % (cmds[id].id, sandbox))
            
            if timeout > 0:
                resource.setrlimit(resource.RLIMIT_CPU, (timeout, timeout))
                return_signal = os.system(cmds[id].command)
                #return_signal = _timeout_command(cmds[id].command, timeout)
            else:
                return_signal = os.system(cmds[id].command)
            
            if sandbox:
                os.chdir("../")
                if clean_sandbox:
                    os.system("rm -rf %d-sandbox-%s" % (cmds[id].id, sandbox))
            
            if return_signal % 256 == 0:
                os._exit(return_signal // 256)
            os._exit(return_signal % 256)

    while len(pids.keys()) > 0:
        (pid, status) = os.wait()
        
        exit_code = status >> 8
        signal_num = status % 256

        time_passed = os.times()[-1] - times.pop(pid)
        old_id = pids.pop(pid)

        cmds[old_id].runtime = time_passed
        cmds[old_id].timed_out = (time_passed >= timeout) and (timeout > 0)
        cmds[old_id].return_code = exit_code
        cmds[old_id].mem_out = (time_passed < timeout) and check_memout(cmds[old_id])

