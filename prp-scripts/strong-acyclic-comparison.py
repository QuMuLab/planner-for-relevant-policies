
from domains import DOMAINS, REDUNDANT_DOMAINS, GOOD_DOMAINS, NEW_DOMAINS, IPC06_DOMAINS, TEST_DOMAINS, INTERESTING_DOMAINS, FOND_DOMAINS

from krrt.utils import get_opts, run_experiment, match_value, get_value, load_CSV, write_file, append_file, read_file

import os, time

USAGE_STRING = """
Usage: python strong-acyclic-comparison.py <TASK> -domain <domain> ...

        Where <TASK> may be:
          run-w1: Run the width 1 experiments
          run-prp-width: Run the experiment to find the width with PRP
          analyze-w1: Analyze the w1 results
          analyze-prp-width: Analyze the prp-width results
        """

if not os.path.exists('settings.py'):
    print "\nNo settings detected. Creating settings.py...\n"
    s =  "TRIALS = 10\n"
    s += "CORES = 1\n"
    s += "MEM_LIMIT = 2000\n"
    s += "TIME_LIMIT = 1800\n"
    s += "SHOW_DATA = True\n"
    write_file('settings.py', s)

from settings import *

BASEDIR = os.path.abspath(os.path.curdir)

MYND_W1 = BASEDIR + "/acyclic-testing/mynd-w1.sh"
MYND_ACYCLIC = BASEDIR + "/acyclic-testing/mynd-acyclic.sh"
MYND_CYCLIC = BASEDIR + "/acyclic-testing/mynd-cyclic.sh"

GRENDEL_W1 = BASEDIR + "/acyclic-testing/grendel-w1.sh"
#GRENDEL_CYCLIC = "/home/cjmuise/Projects/grendel/grendel_astar.py"
GRENDEL_CYCLIC = "/u/cjmuise/EXPERIMENTS/grendel/grendel_astar.py"

PRP_W1 = BASEDIR + "/acyclic-testing/prp-w1.sh"
#PRP_ACYCLIC = "/home/cjmuise/Projects/strong-prp/src/prp --strong"
#PRP_CYCLIC = "/home/cjmuise/Projects/strong-prp/src/prp"
PRP_ACYCLIC = "/u/cjmuise/EXPERIMENTS/strong-prp/src/prp --strong"
PRP_CYCLIC = "/u/cjmuise/EXPERIMENTS/strong-prp/src/prp"

FIP_SC = BASEDIR + "/acyclic-testing/fip-sc.sh"


def check_segfault(outfile):
    return match_value(outfile, '.*Segmentation fault.*')

def check_memout(outfile):
    return match_value(outfile, '.*Memory limit has been reached.*')

def parse_prp(outfile):

    runtime = get_value(outfile, '.*Total time: ([0-9]+\.?[0-9]*)s\n.*', float)
    jic_time = get_value(outfile, '.*Just-in-case Repairs: ([0-9]+\.?[0-9]*)s\n.*', float)
    policy_use_time = get_value(outfile, '.*Using the policy: ([0-9]+\.?[0-9]*)s\n.*', float)
    policy_construction_time = get_value(outfile, '.*Policy Construction: ([0-9]+\.?[0-9]*)s\n.*', float)
    policy_eval_time = get_value(outfile, '.*Evaluating the policy quality: ([0-9]+\.?[0-9]*)s\n.*', float)
    search_time = get_value(outfile, '.*Search Time: ([0-9]+\.?[0-9]*)s\n.*', float)
    engine_init_time = get_value(outfile, '.*Engine Initialization: ([0-9]+\.?[0-9]*)s\n.*', float)
    regression_time = get_value(outfile, '.*Regression Computation: ([0-9]+\.?[0-9]*)s\n.*', float)
    simulator_time = get_value(outfile, '.*Simulator time: ([0-9]+\.?[0-9]*)s\n.*', float)

    successful_states = get_value(outfile, '.*Successful states: ([0-9]+\.?[0-9]*) \+.*', float)
    replans = get_value(outfile, '.*Replans: ([0-9]+\.?[0-9]*) \+.*', float)
    actions = get_value(outfile, '.*Actions: ([0-9]+\.?[0-9]*) \+.*', float)
    size = get_value(outfile, '.*State-Action Pairs: (\d+)\n.*', int)

    strongly_cyclic = match_value(outfile, '.*Strongly Cyclic: True.*')
    succeeded = get_value(outfile, '.*Succeeded: (\d+) .*', int)

    policy_score = get_value(outfile, '.*Policy Score: ([0-9]+\.?[0-9]*)\n.*', float)

    return runtime, jic_time, policy_eval_time, policy_construction_time, policy_use_time, \
           search_time, engine_init_time, regression_time, simulator_time, successful_states, \
           replans, actions, size, strongly_cyclic, succeeded, policy_score




def run_exp(exp_name, domain, solver, dom_probs, check_success, memory=MEM_LIMIT):

    args = ["../%s ../%s" % (item[0], item[1]) for item in dom_probs]

    results = run_experiment(
        base_command = solver,
        single_arguments = {'domprob': args},
        time_limit = TIME_LIMIT,
        memory_limit = memory,
        results_dir = "RESULTS/%s-%s" % (exp_name, domain),
        progress_file = None,
        processors = CORES,
        sandbox = exp_name,
        clean_sandbox = False,
        trials = TRIALS,
        output_file_func = (lambda res: res.single_args['domprob'].split(' ')[1].split('/')[-1]+'.'+str(res.id)+'.out'),
        error_file_func = (lambda res: res.single_args['domprob'].split(' ')[1].split('/')[-1]+'.'+str(res.id)+'.out')
    )

    timeouts = 0
    memouts = 0
    errorouts = 0

    csv = ['domain,problem,runtime,status']

    for res_id in results.get_ids():
        result = results[res_id]
        prob = result.single_args['domprob'].split(' ')[1].split('/')[-1]

        if result.mem_out or check_memout(result.output_file):
            memouts += 1
            csv.append("%s,%s,-1,M" % (domain, prob))

        elif result.timed_out:
            timeouts += 1
            csv.append("%s,%s,-1,T" % (domain, prob))

        #elif not result.clean_run or check_segfault(result.output_file):
        elif not check_success(result.output_file):
            errorouts += 1
            csv.append("%s,%s,-1,E" % (domain, prob))

        else:
            csv.append("%s,%s,%f,-" % (domain, prob, float(result.runtime)))

    print "\nTimed out %d times." % timeouts
    print "Ran out of memory %d times." % memouts
    print "Unknown error %d times." % errorouts
    append_file("RESULTS/%s-%s-results.csv" % (exp_name, domain), csv)


def do_width1_eval(domain):

    def prp_success(out):
        return match_value(out, '.*Strong cyclic plan found\..*')

    def prpa_success(out):
        return match_value(out, '.*Strong Plan Found!.*')

    def grendel_success(out):
        return match_value(out, '.*Strong Cyclic Policy found!.*')

    def mynd_success(out):
        return match_value(out, '.*Strong cyclic plan found\..*')

    def mynda_success(out):
        return match_value(out, '.*The protagonist has got a winning strategy\..*')
    
    def fip_success(out):
        return match_value(out, '.*A strong solution was found!.*')

    domprobs = DOMAINS[domain]

    print "\n\nRunning width-1 experiment for domain %s" % domain

    print "\nTesting PRP (w1, cyclic, acyclic)"
    run_exp('exp_w1--prp_w1', domain, PRP_W1, domprobs, prp_success)
    run_exp('exp_w1--prp_cyclic', domain, PRP_CYCLIC, domprobs, prp_success)
    run_exp('exp_w1--prp_acyclic', domain, PRP_ACYCLIC, domprobs, prpa_success)

    print "\nTesting Grendel (w1, cyclic)"
    run_exp('exp_w1--grendel_w1', domain, GRENDEL_W1, domprobs, grendel_success)
    run_exp('exp_w1--grendel_cyclic', domain, GRENDEL_CYCLIC, domprobs, grendel_success)

    print "\nTesting MyND (w1, cyclic, acyclic)"
    run_exp('exp_w1--mynd_w1', domain, MYND_W1, domprobs, mynd_success, -1)
    run_exp('exp_w1--mynd_cyclic', domain, MYND_CYCLIC, domprobs, mynd_success, -1)
    run_exp('exp_w1--mynd_acyclic', domain, MYND_ACYCLIC, domprobs, mynda_success, -1)
    
    print "\nTesting strongFIP"
    run_exp('exp_w1--fip', domain, FIP_SC, domprobs, fip_success)


def do_prp_width_eval(domain):

    dom_probs = DOMAINS[domain]
    exp_name = "prp-width"

    print "\n\nRunning prp-width experiment for domain %s" % domain

    args = ["../%s ../%s" % (item[0], item[1]) for item in dom_probs]

    results = run_experiment(
        base_command = PRP_ACYCLIC,
        single_arguments = {'domprob': args},
        time_limit = TIME_LIMIT,
        memory_limit = MEM_LIMIT,
        results_dir = "RESULTS/%s-%s" % (exp_name, domain),
        progress_file = None,
        processors = CORES,
        sandbox = exp_name,
        clean_sandbox = False,
        trials = TRIALS,
        output_file_func = (lambda res: res.single_args['domprob'].split(' ')[1].split('/')[-1]+'.'+str(res.id)+'.out'),
        error_file_func = (lambda res: res.single_args['domprob'].split(' ')[1].split('/')[-1]+'.'+str(res.id)+'.err')
    )

    timeouts = 0
    memouts = 0
    errorouts = 0

    csv = ['domain,problem,runtime,status,width']

    for res_id in results.get_ids():
        result = results[res_id]
        prob = result.single_args['domprob'].split(' ')[1].split('/')[-1]

        if match_value(result.output_file, 'No strong plan found.'):
            csv.append("%s,%s,%f,N,-" % (domain, prob, float(result.runtime)))
        else:
            if result.mem_out or check_memout(result.output_file):
                memouts += 1
                csv.append("%s,%s,-1,M,-" % (domain, prob))

            elif result.timed_out:
                timeouts += 1
                csv.append("%s,%s,-1,T,-" % (domain, prob))

            #elif not result.clean_run or check_segfault(result.output_file):
            elif check_segfault(result.output_file):
                errorouts += 1
                csv.append("%s,%s,-1,E,-" % (domain, prob))

            else:
                width = get_value(result.output_file, '.*Width: (\d+)\n.*', int)
                csv.append("%s,%s,%f,-,%d" % (domain, prob, float(result.runtime), width))

    print "\nTimed out %d times." % timeouts
    print "Ran out of memory %d times." % memouts
    print "Unknown error %d times." % errorouts
    append_file("RESULTS/%s-%s-results.csv" % (exp_name, domain), csv)


def analyze_w1(domain):

    prp_acyc_data = load_CSV("RESULTS/exp_w1--prp_acyclic-%s-results.csv" % domain)[1:]
    prp_cyc_data = load_CSV("RESULTS/exp_w1--prp_cyclic-%s-results.csv" % domain)[1:]
    prp_w1_data = load_CSV("RESULTS/exp_w1--prp_w1-%s-results.csv" % domain)[1:]

    mynd_acyc_data = load_CSV("RESULTS/exp_w1--mynd_acyclic-%s-results.csv" % domain)[1:]
    mynd_cyc_data = load_CSV("RESULTS/exp_w1--mynd_cyclic-%s-results.csv" % domain)[1:]
    mynd_w1_data = load_CSV("RESULTS/exp_w1--mynd_w1-%s-results.csv" % domain)[1:]

    grendel_cyc_data = load_CSV("RESULTS/exp_w1--grendel_cyclic-%s-results.csv" % domain)[1:]
    grendel_w1_data = load_CSV("RESULTS/exp_w1--grendel_w1-%s-results.csv" % domain)[1:]
    
    fip_data = load_CSV("RESULTS/exp_w1--fip-%s-results.csv" % domain)[1:]

    probs = set([l[1] for l in prp_w1_data])
    times = {}
    for p in probs:
        times[p] = []
        times[p].append(float(filter(lambda x: p == x[1], prp_w1_data)[0][2]))
        times[p].append(float(filter(lambda x: p == x[1], prp_cyc_data)[0][2]))
        times[p].append(float(filter(lambda x: p == x[1], grendel_w1_data)[0][2]))
        times[p].append(float(filter(lambda x: p == x[1], grendel_cyc_data)[0][2]))
        times[p].append(float(filter(lambda x: p == x[1], mynd_w1_data)[0][2]))
        times[p].append(float(filter(lambda x: p == x[1], mynd_cyc_data)[0][2]))
        times[p].append(float(filter(lambda x: p == x[1], mynd_acyc_data)[0][2]))
        times[p].append(float(filter(lambda x: p == x[1], fip_data)[0][2]))

    scores = [0.0] * 8
    totals = [0.0] * 8
    for p in times:
        best = min(times[p])
        for i in range(8):
            scores[i] += best / times[p][i]
            totals[i] += times[p][i]

    solved = []
    solved.append(float(len(filter(lambda x: '-' == x[-1], prp_w1_data))))
    solved.append(float(len(filter(lambda x: '-' == x[-1], prp_cyc_data))))
    solved.append(float(len(filter(lambda x: '-' == x[-1], grendel_w1_data))))
    solved.append(float(len(filter(lambda x: '-' == x[-1], grendel_cyc_data))))
    solved.append(float(len(filter(lambda x: '-' == x[-1], mynd_w1_data))))
    solved.append(float(len(filter(lambda x: '-' == x[-1], mynd_cyc_data))))
    solved.append(float(len(filter(lambda x: '-' == x[-1], mynd_acyc_data))))
    solved.append(float(len(filter(lambda x: '-' == x[-1], fip_data))))

    print "\n---------------------------"
    print "  Domain:  %s" % domain
    print " # Probs:  %d" % len(prp_acyc_data)

    print "\n Time Scores:"
    print "      PRP W1: %.2f" % scores[0]
    print "     PRP Cyc: %.2f" % scores[1]
    print "  Grendel W1: %.2f" % scores[2]
    print " Grendel Cyc: %.2f" % scores[3]
    print "     MyND W1: %.2f" % scores[4]
    print "    MyND Cyc: %.2f" % scores[5]
    print "   MyND Acyc: %.2f" % scores[6]
    print "         FIP: %.2f" % scores[7]

    print "\n Time totals:"
    print "      PRP W1: %.2f \t/ %d = %.2f" % (totals[0], solved[0], totals[0] / solved[0])
    print "     PRP Cyc: %.2f \t/ %d = %.2f" % (totals[1], solved[1], totals[1] / solved[1])
    print "  Grendel W1: %.2f \t/ %d = %.2f" % (totals[2], solved[2], totals[2] / solved[2])
    print " Grendel Cyc: %.2f \t/ %d = %.2f" % (totals[3], solved[3], totals[3] / solved[3])
    print "     MyND W1: %.2f \t/ %d = %.2f" % (totals[4], solved[4], totals[4] / solved[4])
    print "    MyND Cyc: %.2f \t/ %d = %.2f" % (totals[5], solved[5], totals[5] / solved[5])
    print "   MyND Acyc: %.2f \t/ %d = %.2f" % (totals[6], solved[6], totals[6] / solved[6])
    print "         FIP: %.2f \t/ %d = %.2f" % (totals[7], solved[7], totals[7] / solved[7])

    print "\n      {PRP}"
    print "      W1 Solved: %d" % len(filter(lambda x: '-' == x[-1], prp_w1_data))
    print "     Cyc Solved: %d" % len(filter(lambda x: '-' == x[-1], prp_cyc_data))
    print "  W1 Time / Mem: %d / %d" % (len(filter(lambda x: 'T' == x[-1], prp_w1_data)), len(filter(lambda x: 'M' == x[-1], prp_w1_data)))
    print " Cyc Time / Mem: %d / %d" % (len(filter(lambda x: 'T' == x[-1], prp_cyc_data)), len(filter(lambda x: 'M' == x[-1], prp_cyc_data)))

    print "\n      {Grendel}"
    print "      W1 Solved: %d" % len(filter(lambda x: '-' == x[-1], grendel_w1_data))
    print "     Cyc Solved: %d" % len(filter(lambda x: '-' == x[-1], grendel_cyc_data))
    print "  W1 Time / Mem: %d / %d" % (len(filter(lambda x: 'T' == x[-1], grendel_w1_data)), len(filter(lambda x: 'M' == x[-1], grendel_w1_data)))
    print " Cyc Time / Mem: %d / %d" % (len(filter(lambda x: 'T' == x[-1], grendel_cyc_data)), len(filter(lambda x: 'M' == x[-1], grendel_cyc_data)))

    print "\n      {MyND}"
    print "       W1 Solved: %d" % len(filter(lambda x: '-' == x[-1], mynd_w1_data))
    print "      Cyc Solved: %d" % len(filter(lambda x: '-' == x[-1], mynd_cyc_data))
    print "     Acyc Solved: %d" % len(filter(lambda x: '-' == x[-1], mynd_acyc_data))
    print "   W1 Time / Mem: %d / %d" % (len(filter(lambda x: 'T' == x[-1], mynd_w1_data)), len(filter(lambda x: 'M' == x[-1], mynd_w1_data)))
    print "  Cyc Time / Mem: %d / %d" % (len(filter(lambda x: 'T' == x[-1], mynd_cyc_data)), len(filter(lambda x: 'M' == x[-1], mynd_cyc_data)))
    print " Acyc Time / Mem: %d / %d" % (len(filter(lambda x: 'T' == x[-1], mynd_acyc_data)), len(filter(lambda x: 'M' == x[-1], mynd_acyc_data)))

    print "\n      {FIP}"
    print "      Solved: %d" % len(filter(lambda x: '-' == x[-1], fip_data))
    print "  Time / Mem: %d / %d" % (len(filter(lambda x: 'T' == x[-1], fip_data)), len(filter(lambda x: 'M' == x[-1], fip_data)))


    print

def analyze_prp_width(domain):
    data = load_CSV("RESULTS/prp-width-%s-results.csv" % domain)[1:]

    found = len(filter(lambda x: '-' != x[-1], data))

    print "\n---------------------------"
    print "  Domain:  %s" % domain
    print " # Probs:  %d" % len(data)
    print "  Memout:  %d" % len(filter(lambda x: 'M' == x[-2], data))
    print " Timeout:  %d" % len(filter(lambda x: 'T' == x[-2], data))
    print "   Error:  %d" % len(filter(lambda x: 'E' == x[-2], data))
    print " No plan:  %d" % len(filter(lambda x: 'N' == x[-2], data))
    print " # w < 6:  %d" % len(filter(lambda x: '-' != x[-1], data))

    if found > 0:
        print "\n   Width Counts"
        for i in range(1, 6):
            found = len(filter(lambda x: str(i) == x[-1], data))
            if found > 0:
                print "     w=%d:  %d" % (i, found)

    print "---------------------------\n"


if __name__ == '__main__':
    myargs, flags = get_opts()

    if not os.path.exists('RESULTS'):
        os.makedirs('RESULTS')

    if '-trials' in myargs:
        TRIALS = int(myargs['-trials'])

    if '-domain' not in myargs:
        print "Error: Must choose a domain:"
        print USAGE_STRING
        os._exit(1)

    if 'all' == myargs['-domain']:
        doms = GOOD_DOMAINS
    else:
        doms = [myargs['-domain']]

    if 'run-w1' in flags:
        for dom in doms:
            do_width1_eval(dom)

    if 'run-prp-width' in flags:
        for dom in doms:
            do_prp_width_eval(dom)

    if 'analyze-w1' in flags:
        for dom in doms:
            analyze_w1(dom)

    if 'analyze-prp-width' in flags:
        for dom in doms:
            analyze_prp_width(dom)

