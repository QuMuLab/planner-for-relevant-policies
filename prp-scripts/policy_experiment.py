
from domains import DOMAINS, REDUNDANT_DOMAINS, GOOD_DOMAINS, NEW_DOMAINS, IPC06_DOMAINS, TEST_DOMAINS, INTERESTING_DOMAINS, FOND_DOMAINS

from krrt.utils import get_opts, run_experiment, match_value, get_value, load_CSV, write_file, append_file, read_file

import os, time

USAGE_STRING = """
Usage: python policy_experiment.py <TASK> -domain <domain> ...

        Where <TASK> may be:
          full: Run all experiment parameters
          fip-vs-prp: Run a comparison between fip and the best setting for PRP
          ffreplan-vs-prp: Run a comparison between ffreplan and prp in online mode
          fip: Just run fip on the given domains
          prp: Just run prp on the given domains
          jic: Test the varied jic limit (must specify -problem and -limit)
          redundant: Run the comparison for domains that have redundancy
          ablation: Run with various features disabled to see the impact they have.
          test: Run a complete test of all parameter settings (make sure to limit the domains)
          test-planlocal: Test the impact of the various planlocal settings
          test-deadend: Test the impact of the various deadend settings
          test-optscd: Test the impact of optimized-scd
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

PARAMETERS = ['jic-limit',
              'trials',
              'forgetpolicy',
              'fullstate',
              'planlocal',
              'partial-planlocal',
              'plan-with-policy',
              'limit-planlocal',
              'detect-deadends',
              'generalize-deadends',
              'online-deadends',
              'optimized-scd']

PRP_PARAMS = {'best': { '--jic-limit': [18000],
                        '--trials': [100],
                        '--forgetpolicy': [0],
                        '--fullstate': [0],
                        '--planlocal': [1],
                        '--partial-planlocal': [1],
                        '--plan-with-policy': [1],
                        '--limit-planlocal': [1],
                        '--detect-deadends': [1],
                        '--generalize-deadends': [1],
                        '--online-deadends': [1],
                        '--optimized-scd': [1]},

              'no-local': { '--jic-limit': [18000],
                        '--trials': [100],
                        '--forgetpolicy': [0],
                        '--fullstate': [0],
                        '--planlocal': [1],
                        '--partial-planlocal': [0],
                        '--plan-with-policy': [1],
                        '--limit-planlocal': [0],
                        '--detect-deadends': [1],
                        '--generalize-deadends': [1],
                        '--online-deadends': [1],
                        '--optimized-scd': [1]},

              'no-scd': { '--jic-limit': [18000],
                        '--trials': [100],
                        '--forgetpolicy': [0],
                        '--fullstate': [0],
                        '--planlocal': [1],
                        '--partial-planlocal': [1],
                        '--plan-with-policy': [1],
                        '--limit-planlocal': [1],
                        '--detect-deadends': [1],
                        '--generalize-deadends': [1],
                        '--online-deadends': [1],
                        '--optimized-scd': [0]},

              'no-dead': { '--jic-limit': [18000],
                        '--trials': [100],
                        '--forgetpolicy': [0],
                        '--fullstate': [0],
                        '--planlocal': [1],
                        '--partial-planlocal': [1],
                        '--plan-with-policy': [1],
                        '--limit-planlocal': [1],
                        '--detect-deadends': [1],
                        '--generalize-deadends': [0],
                        '--online-deadends': [0],
                        '--optimized-scd': [1]},

              'no-partial': { '--jic-limit': [18000],
                           '--trials': [100],
                           '--forgetpolicy': [0],
                           '--fullstate': [1],
                           '--planlocal': [1],
                           '--partial-planlocal': [0],
                           '--plan-with-policy': [1],
                           '--limit-planlocal': [1],
                           '--detect-deadends': [1],
                           '--generalize-deadends': [0],
                           '--online-deadends': [1],
                           '--optimized-scd': [1]},

              'jic':  { '--jic-limit': [],
                        '--trials': [0],
                        '--forgetpolicy': [0],
                        '--fullstate': [0],
                        '--planlocal': [1],
                        '--partial-planlocal': [1],
                        '--plan-with-policy': [1],
                        '--limit-planlocal': [1],
                        '--detect-deadends': [1],
                        '--generalize-deadends': [1],
                        '--online-deadends': [1],
                        '--optimized-scd': [1]},

              'full': { '--jic-limit': [18000],
                        '--trials': [100],
                        '--forgetpolicy': [0],
                        '--fullstate': [0],
                        '--planlocal': [0,1],
                        '--partial-planlocal': [0,1],
                        '--plan-with-policy': [1],
                        '--limit-planlocal': [0,1],
                        '--detect-deadends': [0,1],
                        '--generalize-deadends': [0,1],
                        '--online-deadends': [0,1],
                        '--optimized-scd': [0,1]},

              'best-online': { '--jic-limit': [0],
                               '--trials': [100],
                               '--forgetpolicy': [1],
                               '--fullstate': [0],
                               '--planlocal': [1],
                               '--partial-planlocal': [1],
                               '--plan-with-policy': [1],
                               '--limit-planlocal': [1],
                               '--detect-deadends': [0],
                               '--generalize-deadends': [0],
                               '--online-deadends': [0],
                               '--optimized-scd': [0]},

              'ffreplan': { '--jic-limit': [0],
                            '--trials': [100],
                            '--forgetpolicy': [1],
                            '--fullstate': [1],
                            '--planlocal': [0],
                            '--partial-planlocal': [0],
                            '--plan-with-policy': [1],
                            '--limit-planlocal': [0],
                            '--detect-deadends': [0],
                            '--generalize-deadends': [0],
                            '--online-deadends': [0],
                            '--optimized-scd': [0]},

              'redundant': { '--jic-limit': [18000],
                             '--trials': [100],
                             '--forgetpolicy': [0],
                             '--fullstate': [0,1],
                             '--planlocal': [0,1],
                             '--partial-planlocal': [0],
                             '--plan-with-policy': [1],
                             '--limit-planlocal': [0],
                             '--detect-deadends': [0],
                             '--generalize-deadends': [0],
                             '--online-deadends': [0],
                             '--optimized-scd': [0]},

              'planlocal': { '--jic-limit': [18000],
                             '--trials': [100],
                             '--forgetpolicy': [0],
                             '--fullstate': [0],
                             '--planlocal': [0,1],
                             '--partial-planlocal': [0,1],
                             '--plan-with-policy': [1],
                             '--limit-planlocal': [0,1],
                             '--detect-deadends': [1],
                             '--generalize-deadends': [1],
                             '--online-deadends': [1],
                             '--optimized-scd': [1]},

              'test': { '--jic-limit': [0,18000],
                        '--trials': [10],
                        '--forgetpolicy': [0,1],
                        '--fullstate': [0,1],
                        '--planlocal': [0,1],
                        '--partial-planlocal': [0,1],
                        '--plan-with-policy': [0,1],
                        '--limit-planlocal': [0,1],
                        '--detect-deadends': [0,1],
                        '--generalize-deadends': [0,1],
                        '--online-deadends': [0,1],
                        '--optimized-scd': [0,1]}
             }


def parse_fip(outfile):
    runtime = get_value(outfile, '.* ([0-9]+\.?[0-9]+) seconds searching.*', float)
    policy_size = len(filter(lambda x: 'case S' in x, read_file(outfile)))
    return runtime, policy_size

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


def parse_prp_settings(res):
    return ','.join([res.parameters['--' + p] for p in PARAMETERS])

def doit(domain, dofip = True, doprp = True, redundant = 0, prp_params = PRP_PARAMS['full'], exp_name = ''):

    if 'all' == domain:
        for dom in GOOD_DOMAINS:
            doit(dom, dofip=dofip, doprp=doprp, prp_params=prp_params, exp_name=exp_name)
        return

    elif 'new' == domain:
        for dom in NEW_DOMAINS:
            doit(dom, dofip=dofip, doprp=doprp, prp_params=prp_params, exp_name=exp_name)
        return

    elif 'fond' == domain:
        for dom in FOND_DOMAINS:
            doit(dom, dofip=dofip, doprp=doprp, prp_params=prp_params, exp_name=exp_name)
        return

    elif 'ipc' == domain:
        for dom in IPC06_DOMAINS:
            doit(dom, dofip=dofip, doprp=doprp, prp_params=prp_params, exp_name=exp_name)
        return

    elif 'test' == domain:
        for dom in TEST_DOMAINS:
            doit(dom, dofip=dofip, doprp=doprp, prp_params=prp_params, exp_name=exp_name)
        return

    elif 'interesting' == domain:
        for dom in INTERESTING_DOMAINS:
            doit(dom, dofip=dofip, doprp=doprp, prp_params=prp_params, exp_name=exp_name)
        return

    if redundant > 0:
        dom_probs = REDUNDANT_DOMAINS[domain][redundant]
        doit_prp("%s-redundant-%d" % (domain, redundant), dom_probs, PRP_PARAMS['redundant'])

    else:
        dom_probs = DOMAINS[domain]

        if '' != exp_name:
            exp_name += '-'

        if dofip:
            doit_fip(domain, dom_probs, exp_name+'fip')

        if doprp:
            doit_prp(domain, dom_probs, prp_params, exp_name+'prp')

def doit_fip(domain, dom_probs, exp_name = 'fip'):

    print "\n\nRunning FIP experiments on domain, %s" % domain

    fip_args = ["-o ../%s.fip -f ../%s" % (item[0], item[1]) for item in dom_probs]

    fip_results = run_experiment(
        base_command = './../fip',
        single_arguments = {'domprob': fip_args},
        time_limit = TIME_LIMIT,
        memory_limit = MEM_LIMIT,
        results_dir = "RESULTS/%s-%s" % (exp_name, domain),
        progress_file = None,
        processors = CORES,
        sandbox = exp_name,
        clean_sandbox = True,
        output_file_func = (lambda res: res.single_args['domprob'].split('/')[-1]+'.out'),
        error_file_func = (lambda res: res.single_args['domprob'].split('/')[-1]+'.err')
    )

    timeouts = 0
    memouts = 0
    errorouts = 0
    fip_csv = ['domain,problem,runtime,size,status']
    for res_id in fip_results.get_ids():
        result = fip_results[res_id]
        prob = result.single_args['domprob'].split(' ')[3].split('/')[-1]

        if match_value(result.output_file, 'No plan will solve it') or 'No solutions are found!' in read_file(result.output_file)[-1]:
            fip_csv.append("%s,%s,-1,-1,N" % (domain, prob))
        else:
            if result.timed_out:
                timeouts += 1
                fip_csv.append("%s,%s,-1,-1,T" % (domain, prob))
            elif result.mem_out:
                memouts += 1
                fip_csv.append("%s,%s,-1,-1,M" % (domain, prob))
            elif not result.clean_run or check_segfault(result.output_file):
                errorouts += 1
                fip_csv.append("%s,%s,-1,-1,E" % (domain, prob))
            else:
                run, size = parse_fip(result.output_file)
                fip_csv.append("%s,%s,%f,%d,-" % (domain, prob, run, size))

    print "\nTimed out %d times." % timeouts
    print "Ran out of memory %d times." % memouts
    print "Unknown error %d times." % errorouts
    append_file("RESULTS/%s-%s-results.csv" % (exp_name, domain), fip_csv)


def doit_prp(domain, dom_probs, prp_params, exp_name = 'prp'):

    print "\n\nRunning %s experiments on domain, %s" % (exp_name, domain)

    prp_args = ["../%s ../%s" % (item[0], item[1]) for item in dom_probs]

    prp_results = run_experiment(
        base_command = './../../src/prp',
        single_arguments = {'domprob': prp_args},
        parameters = prp_params,
        time_limit = TIME_LIMIT,
        memory_limit = MEM_LIMIT,
        results_dir = "RESULTS/%s-%s" % (exp_name, domain),
        progress_file = None,
        processors = CORES,
        sandbox = exp_name,
        clean_sandbox = True,
        trials = TRIALS,
        output_file_func = (lambda res: res.single_args['domprob'].split(' ')[1].split('/')[-1]+'.'+str(res.id)+'.out'),
        error_file_func = (lambda res: res.single_args['domprob'].split(' ')[1].split('/')[-1]+'.'+str(res.id)+'.err')
    )

    timeouts = 0
    memouts = 0
    errorouts = 0
    parametererrors = 0
    prp_csv = ['domain,problem,runtime,size,status,%s,jic time,policy eval,policy creation,policy use,search time,engine time,regression time,simulator time,successful states,replans,actions,policy score,strongly cyclic,succeeded' % ','.join(PARAMETERS)]
    for res_id in prp_results.get_ids():
        result = prp_results[res_id]
        prob = result.single_args['domprob'].split(' ')[1].split('/')[-1]

        if match_value(result.output_file, 'No solution -- aborting repairs.'):
            prp_csv.append("%s,%s,-1,-1,N,%s,%s" % (domain, prob, parse_prp_settings(result), ','.join(['-']*14)))
        else:
            if result.mem_out or check_memout(result.output_file):
                memouts += 1
                prp_csv.append("%s,%s,-1,-1,M,%s,%s" % (domain, prob, parse_prp_settings(result), ','.join(['-']*14)))

            elif result.timed_out:
                timeouts += 1
                prp_csv.append("%s,%s,-1,-1,T,%s,%s" % (domain, prob, parse_prp_settings(result), ','.join(['-']*14)))

            #elif not result.clean_run or check_segfault(result.output_file):
            elif check_segfault(result.output_file):
                errorouts += 1
                prp_csv.append("%s,%s,-1,-1,E,%s,%s" % (domain, prob, parse_prp_settings(result), ','.join(['-']*14)))

            elif match_value(result.output_file, '.*Parameter Error.*'):
                parametererrors += 1
                prp_csv.append("%s,%s,-1,-1,P,%s,%s" % (domain, prob, parse_prp_settings(result), ','.join(['-']*14)))

            else:
                runtime, jic_time, policy_eval_time, policy_construction_time, policy_use_time, \
                search_time, engine_init_time, regression_time, simulator_time, successful_states, \
                replans, actions, size, strongly_cyclic, succeeded, policy_score = parse_prp(result.output_file)

                prp_csv.append("%s,%s,%f,%d,-,%s,%f,%f,%f,%f,%f,%f,%f,%f,%d,%d,%d,%f,%s,%s" % (domain, prob,
                                                            runtime, size, parse_prp_settings(result),
                                                            jic_time, policy_eval_time, policy_construction_time, policy_use_time,
                                                            search_time, engine_init_time, regression_time, simulator_time,
                                                            successful_states, replans, actions, policy_score,
                                                            str(strongly_cyclic), str(succeeded)))

    print "\nTimed out %d times." % timeouts
    print "Ran out of memory %d times." % memouts
    print "Unknown error %d times." % errorouts
    print "Invalid parameter settings %d times." % parametererrors
    append_file("RESULTS/%s-%s-results.csv" % (exp_name, domain), prp_csv)


def dojic(dom, prob, max_jic):
    print "Running a varied jic experiment for the following domain / problem:"
    print dom
    print prob

    exp_name = "jic"
    domain = dom.split('/')[-2]

    PRP_PARAMS['jic']['--jic-limit'] = list(range(1, max_jic+1))

    prp_results = run_experiment(
        base_command = './../../src/prp',
        single_arguments = {'domprob': ["../%s ../%s" % (dom, prob)]},
        parameters = PRP_PARAMS['jic'],
        time_limit = TIME_LIMIT,
        memory_limit = MEM_LIMIT,
        results_dir = "RESULTS/%s-%s" % (exp_name, domain),
        progress_file = None,
        processors = CORES,
        sandbox = exp_name,
        clean_sandbox = True,
        trials = TRIALS,
        output_file_func = (lambda res: res.single_args['domprob'].split(' ')[1].split('/')[-1]+'.'+str(res.id)+'.out'),
        error_file_func = (lambda res: res.single_args['domprob'].split(' ')[1].split('/')[-1]+'.'+str(res.id)+'.err')
    )

    prp_csv = ['jic limit,jic time,policy score']
    for res_id in prp_results.get_ids():
        result = prp_results[res_id]
        jic_lim = result.parameters['--jic-limit']
        jic_time = get_value(result.output_file, '.*Just-in-case Repairs: ([0-9]+\.?[0-9]*)s\n.*', float)
        policy_score = get_value(result.output_file, '.*Policy Score: ([0-9]+\.?[0-9]*)\n.*', float)

        prp_csv.append("%s,%f,%f" % (jic_lim, jic_time, policy_score))

    append_file("RESULTS/%s-%s-results.csv" % (exp_name, domain), prp_csv)

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

    if 'ablation' in flags:
        for ab in ['no-local', 'no-dead', 'no-scd', 'no-partial', 'best']:
            doit(myargs['-domain'], dofip=False, doprp=True, prp_params=PRP_PARAMS[ab], exp_name=ab)

    if 'full' in flags:
        doit(myargs['-domain'])

    if 'test-planlocal' in flags:
        doit(myargs['-domain'], dofip=False, doprp=True, prp_params = PRP_PARAMS['planlocal'])

    if 'test' in flags:
        TRIALS = 1
        doit(myargs['-domain'], dofip=False, doprp=True, prp_params = PRP_PARAMS['test'])

    if 'prp' in flags:
        doit(myargs['-domain'], dofip=False, doprp=True, prp_params = PRP_PARAMS['best'])

    if 'ffreplan-vs-prp' in flags:
        if '-redundant' in myargs:
            dom_probs = REDUNDANT_DOMAINS[myargs['-domain']][int(myargs['-redundant'])]
            doit_prp("%s-redundant-%s" % (myargs['-domain'], myargs['-redundant']), dom_probs, PRP_PARAMS['best-online'], exp_name='bo-prp')
            doit_prp("%s-redundant-%s" % (myargs['-domain'], myargs['-redundant']), dom_probs, PRP_PARAMS['ffreplan'], exp_name='ffr-prp')
        else:
            doit(myargs['-domain'], dofip=False, doprp=True, prp_params = PRP_PARAMS['best-online'], exp_name='bo')
            doit(myargs['-domain'], dofip=False, doprp=True, prp_params = PRP_PARAMS['ffreplan'], exp_name='ffr')

    if 'fip' in flags:
        doit(myargs['-domain'], dofip=True, doprp=False)

    if 'fip-vs-prp' in flags:
        doit(myargs['-domain'], prp_params = PRP_PARAMS['best'])

    if 'redundant' in flags:
        for i in REDUNDANT_DOMAINS[myargs['-domain']].keys():
            doit(myargs['-domain'], redundant = i)

    if 'jic' in flags:
        if '-problem' not in myargs:
            print "Error: Must choose a problem:"
            print USAGE_STRING
            os._exit(1)
        if '-limit' not in myargs:
            print "Error: Must choose a limit:"
            print USAGE_STRING
            os._exit(1)

        dojic(myargs['-domain'], myargs['-problem'], int(myargs['-limit']))
