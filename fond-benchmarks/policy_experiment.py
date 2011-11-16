
from domains import DOMAINS, REDUNDANT_DOMAINS, GOOD_DOMAINS, NEW_DOMAINS, IPC06_DOMAINS

from krrt.utils import get_opts, run_experiment, match_value, get_value, load_CSV, write_file, append_file, read_file

import os, time

USAGE_STRING = """
Usage: python policy_experiment.py <TASK> -domain <domain> ...

        Where <TASK> may be:
          full: Run all experiment parameters
          fip-vs-prp: Run a comparison between fip and the best setting for PRP
          fip: Just run fip on the given domains
          redundant: Run the comparison for domains that have redundancy
        """

TRIALS = 5
CORES = 16
MEM_LIMIT = 2000
TIME_LIMIT = 1800
SHOW_DATA = True
BASEDIR = os.path.abspath(os.path.curdir)

PRP_PARAMS = {'all': {'--jic-limit': [18000],
                      '--forgetpolicy': [0],
                      '--fullstate': [0,1],
                      '--planlocal': [0,1],
                      '--detect-deadends': [0,1],
                      '--trials': [100],
                      '--plan-with-policy': [0,1]},

              'best': {'--jic-limit': [18000],
                       '--forgetpolicy': [0],
                       '--fullstate': [0],
                       '--planlocal': [0,1],
                       '--detect-deadends': [1],
                       '--trials': [100],
                       '--plan-with-policy': [1]},
              
              'ffreplan': {'--jic-limit': [0],
                           '--forgetpolicy': [1],
                           '--fullstate': [1],
                           '--planlocal': [0],
                           '--trials': [100],
                           '--plan-with-policy': [1]},
              
              'redundant': {'--jic-limit': [18000],
                            '--forgetpolicy': [0],
                            '--fullstate': [0,1],
                            '--planlocal': [0,1],
                            '--trials': [100],
                            '--plan-with-policy': [1]}
             }


def parse_fip(outfile):
    runtime = get_value(outfile, '.* ([0-9]+\.?[0-9]+) seconds searching.*', float)
    policy_size = len(filter(lambda x: 'case S' in x, read_file(outfile)))
    return runtime, policy_size

def parse_prp(outfile):
    
    runtime = get_value(outfile, '.*Total time: ([0-9]+\.?[0-9]*)s\n.*', float)
    jic_time = get_value(outfile, '.*Just-in-case Repairs: ([0-9]+\.?[0-9]*)s\n.*', float)
    policy_eval_time = get_value(outfile, '.*Using the policy: ([0-9]+\.?[0-9]*)s\n.*', float)
    policy_construction_time = get_value(outfile, '.*Policy Construction: ([0-9]+\.?[0-9]*)s\n.*', float)
    search_time = get_value(outfile, '.*Search Time: ([0-9]+\.?[0-9]*)s\n.*', float)
    engine_init_time = get_value(outfile, '.*Engine Initialization: ([0-9]+\.?[0-9]*)s\n.*', float)
    regression_time = get_value(outfile, '.*Regression Computation: ([0-9]+\.?[0-9]*)s\n.*', float)
    
    successful_states = get_value(outfile, '.*Successful states: ([0-9]+\.?[0-9]*) \+.*', float)
    replans = get_value(outfile, '.*Replans: ([0-9]+\.?[0-9]*) \+.*', float)
    actions = get_value(outfile, '.*Actions: ([0-9]+\.?[0-9]*) \+.*', float)
    size = get_value(outfile, '.*State-Action Pairs: (\d+)\n.*', int)
    
    strongly_cyclic = match_value(outfile, '.*Strongly Cyclic: True.*')
    succeeded = get_value(outfile, '.*Succeeded: (\d+) .*', int)
    
    return runtime, jic_time, policy_eval_time, policy_construction_time, \
           search_time, engine_init_time, regression_time, successful_states, \
           replans, actions, size, strongly_cyclic, succeeded
    

def parse_prp_settings(res):
    return ','.join([res.parameters[p] for p in ['--jic-limit', '--forgetpolicy', '--fullstate', '--planlocal', '--plan-with-policy']])

def doit(domain, dofip = True, doprp = True, redundant = 0, prp_params = PRP_PARAMS['all']):
    
    if 'all' == domain:
        for dom in GOOD_DOMAINS:
            doit(dom, dofip=dofip, doprp=doprp, prp_params=prp_params)
        return
    
    elif 'new' == domain:
        for dom in NEW_DOMAINS:
            doit(dom, dofip=dofip, doprp=doprp, prp_params=prp_params)
        return
    
    elif 'fond' == domain:
        for dom in FOND_DOMAINS:
            doit(dom, dofip=dofip, doprp=doprp, prp_params=prp_params)
        return

    if redundant > 0:
        dom_probs = REDUNDANT_DOMAINS[domain][redundant]
        doit_prp("%s-redundant-%d" % (domain, redundant), dom_probs, PRP_PARAMS['redundant'])
    
    else:
        dom_probs = DOMAINS[domain]
        
        if dofip:
            doit_fip(domain, dom_probs)
        
        if doprp:
            doit_prp(domain, dom_probs, prp_params)

def doit_fip(domain, dom_probs):
    
    print "\n\nRunning FIP experiments on domain, %s" % domain
    
    fip_args = ["-o ../%s.fip -f ../%s" % (item[0], item[1]) for item in dom_probs]
    
    fip_results = run_experiment(
        base_command = './../fip',
        single_arguments = {'domprob': fip_args},
        time_limit = TIME_LIMIT,
        memory_limit = MEM_LIMIT,
        results_dir = "RESULTS/fip-%s" % domain,
        progress_file = None,
        processors = CORES,
        sandbox = 'fip',
        output_file_func = (lambda res: res.single_args['domprob'].split('/')[-1]+'.out'),
        error_file_func = (lambda res: res.single_args['domprob'].split('/')[-1]+'.err')
    )
    
    timeouts = 0
    memouts = 0
    fip_csv = ['domain,problem,runtime,size,status']
    for res_id in fip_results.get_ids():
        result = fip_results[res_id]
        prob = result.single_args['domprob'].split(' ')[3].split('/')[-1]
        
        if match_value(result.output_file, 'No plan will solve it'):
            fip_csv.append("%s,%s,-1,-1,N" % (domain, prob))
        else:
            if result.timed_out:
                timeouts += 1
                fip_csv.append("%s,%s,-1,-1,T" % (domain, prob))
            elif result.mem_out:
                memouts += 1
                fip_csv.append("%s,%s,-1,-1,M" % (domain, prob))
            else:
                run, size = parse_fip(result.output_file)
                fip_csv.append("%s,%s,%f,%d,-" % (domain, prob, run, size))
    
    print "\nTimed out %d times." % timeouts
    print "Ran out of memory %d times.\n" % memouts
    write_file("RESULTS/fip-%s-results.csv" % domain, fip_csv)
    

def doit_prp(domain, dom_probs, prp_params):
    
    print "\n\nRunning PRP experiments on domain, %s" % domain
    
    prp_args = ["../%s ../%s RES" % (item[0], item[1]) for item in dom_probs]
    
    prp_results = run_experiment(
        base_command = './../../src/plan-prp',
        single_arguments = {'domprob': prp_args},
        parameters = prp_params,
        time_limit = TIME_LIMIT,
        memory_limit = MEM_LIMIT,
        results_dir = "RESULTS/prp-%s" % domain,
        progress_file = None,
        processors = CORES,
        sandbox = 'prp',
        trials = TRIALS,
        output_file_func = (lambda res: res.single_args['domprob'].split(' ')[1].split('/')[-1]+'.'+str(res.id)+'.out'),
        error_file_func = (lambda res: res.single_args['domprob'].split(' ')[1].split('/')[-1]+'.'+str(res.id)+'.err')
    )
    
    timeouts = 0
    memouts = 0
    prp_csv = ['domain,problem,runtime,size,status,jic-limit,forgetpolicy,fullstate,planlocal,usepolicy,jic time,policy eval,policy creation,search time,engine time,regression time,successful states,replans,actions,strongly cyclic,succeeded']
    for res_id in prp_results.get_ids():
        result = prp_results[res_id]
        prob = result.single_args['domprob'].split(' ')[1].split('/')[-1]
        
        if match_value(result.output_file, 'No solution -- aborting repairs.'):
            prp_csv.append("%s,%s,-1,-1,N,%s,%s" % (domain, prob, parse_prp_settings(result), ','.join(['-']*11)))
        else:
            if result.mem_out:
                memouts += 1
                prp_csv.append("%s,%s,-1,-1,M,%s,%s" % (domain, prob, parse_prp_settings(result), ','.join(['-']*11)))
            
            elif result.timed_out:
                timeouts += 1
                prp_csv.append("%s,%s,-1,-1,T,%s,%s" % (domain, prob, parse_prp_settings(result), ','.join(['-']*11)))
              
            else:
                runtime, jic_time, policy_eval_time, policy_construction_time, \
                    search_time, engine_init_time, regression_time, successful_states, \
                    replans, actions, size, strongly_cyclic, succeeded = parse_prp(result.output_file)
                prp_csv.append("%s,%s,%f,%d,-,%s,%f,%f,%f,%f,%f,%f,%d,%d,%d,%s,%s" % (domain, prob,
                                                            runtime, size, parse_prp_settings(result),
                                                            jic_time, policy_eval_time, policy_construction_time,
                                                            search_time, engine_init_time, regression_time,
                                                            successful_states, replans, actions,
                                                            str(strongly_cyclic), str(succeeded)))
    
    print "\nTimed out %d times." % timeouts
    print "Ran out of memory %d times.\n" % memouts
    write_file("RESULTS/prp-%s-results.csv" % domain, prp_csv)


if __name__ == '__main__':
    myargs, flags = get_opts()
    
    if '-domain' not in myargs:
        print "Error: Must choose a domain:"
        print USAGE_STRING
        os._exit(1)
    
    if 'full' in flags:
        doit(myargs['-domain'])
    
    if 'fip' in flags:
        doit(myargs['-domain'], dofip=True, doprp=False)
    
    if 'fip-vs-prp' in flags:
        doit(myargs['-domain'], prp_params = PRP_PARAMS['best'])
    
    if 'redundant' in flags:
        for i in REDUNDANT_DOMAINS[myargs['-domain']].keys():
            doit(myargs['-domain'], redundant = i)
