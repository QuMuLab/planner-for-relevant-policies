
import os
from krrt.utils import fileio, run_experiment, get_opts, get_value, write_file

domain = get_opts()[0]['-domain']

problems = fileio.read_file("%s/pmap" % domain)
domprobs = ["../%s/domain.pddl ../%s/%s OUT --jic-limit 10" % (domain, domain, prob) for prob in problems]

results = run_experiment(
    base_directory = ".",
    base_command = './../../src/plan-prp',
    single_arguments = {'domprob': domprobs},
    time_limit = 1800, # 15minute time limit (900 seconds)
    memory_limit = 1000, # 1gig memory limit (1000 megs)
    results_dir = "%s/results" % domain,
    progress_file = None, # Print the progress to stdout
    processors = 6, # You've got 8 cores, right?
    sandbox = 'fd_out',
    clean_sandbox = False
)

good_results = results.filter(lambda result: not result.timed_out)
good_results = [good_results[i] for i in good_results.get_ids()]

print "Coverage: %d / %d" % (len(good_results), len(domprobs))

try:
    data = ['runtime(s),size(nodes)'] + ["%f,%d" % (res.runtime, get_value(res.output_file, '.*State-Action Pairs: (\d+)\n.*', int)) for res in good_results]
except:
    pass

write_file("%s.csv" % domain, data)


