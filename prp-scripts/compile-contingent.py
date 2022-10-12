
from external.utils import get_opts, match_value, get_value, write_file, append_file, run_command, read_file, get_lines

import os, time, glob, sys

USAGE_STRING = """
Usage: python compile-contingent.py <converter> -ind <old domain> -inp <old problem> -outd <new domain> -outp <new problem>

        Additional Options:
          <converter>: Either cf2cs or kreplanner
          
        """

MEMLIMIT = 2000
TIMELIMIT = 1800

bad_strings = set(['FOO', # Dummy predicates introduced by cf2cs
                   'FALSE',
                   'ACTIVE',
                   'ALL_END',
                   'DUMMY',
                   'CLOSURE',
                   '(o_', # Observation predicates not required
                   'ver0',
                   'ver1',
                   'DETDUP',
                   ':action sensor',
                   'invariant'
                  ])

def convert_cf2cs(ind = 'domain-cf2cs.pddl', inp = 'problem-cf2cs.pddl', outd = 'out-dom.pddl', outp = 'out-prob.pddl'):
    
    # Do the initial conversion
    print("Running the following command...")
    cf2cs_string = "./cf2cs -t0 -mac -cond -ckinl -ckit -cdisjk0 -fp -cnap -cnamac -sn -tsn %s %s" % (ind, inp)
    print(cf2cs_string)
    run_command(cf2cs_string, MEMLIMIT=MEMLIMIT, TIMELIMIT=TIMELIMIT)
    print()
    
    
    domain_lines = read_file('new-d.pddl')
    problem_lines = read_file('new-p.pddl')
    
    
    # Strip out the nonsense fluents
    print("Stripping out the unused fluents...")
    for word in bad_strings:
        domain_lines = [x for x in domain_lines if word not in x]
        problem_lines = [x for x in problem_lines if word not in x]
    print()
    
    
    # Convert the observation actions
    print("Converting observations to non-deterministic actions...")
    
    # Count the observation actions
    obs_count = len([x for x in domain_lines if '(:observation' in x])
    obs_preds = ["(CAN_OBSERVE_%d)" % (d+1) for d in range(obs_count)]
    current_obs = 0
    
    in_obs = False
    for i in range(len(domain_lines)):
        
        # Add any new predicates
        if '(:predicates' in domain_lines[i]:
            domain_lines[i] = domain_lines[i] + "\n" + "\n".join(["    %s" % o for o in obs_preds])
        
        # Convert the observation to non-det action
        if '(:observation' in domain_lines[i]:
            domain_lines[i] = '(:action'.join(domain_lines[i].split('(:observation'))
            current_obs += 1
            if ':precondition' in domain_lines[i+1]:
                domain_lines[i+2] = "      (and (CAN_OBSERVE_%d) %s)" % (current_obs, domain_lines[i+2].strip())
            else:
                domain_lines[i] = domain_lines[i] + "\n    :precondition\n      (CAN_OBSERVE_%d)" % current_obs
        
        # Convert the effect
        if ':branches (or ' in domain_lines[i]:
            domain_lines[i] = (":effect (and (not (CAN_OBSERVE_%d)) (oneof" % current_obs).join(domain_lines[i].split(':branches (or '))
            in_obs = True
        
        # Close a non-det effect
        if in_obs and '    )' == domain_lines[i]:
            domain_lines[i] += ')'
            in_obs = False
            
    # Fix the problem file to have the new fluents
    problem_lines = problem_lines[:3] + ["\n".join(["    %s" % o for o in obs_preds])] + problem_lines[3:]
    print()
    
    # Write output and clean up
    print("Writing new domain / problem and cleaning up...")
    write_file(outd, domain_lines)
    write_file(outp, problem_lines)
    os.system('rm new-d.pddl')
    os.system('rm new-p.pddl')
    print()


def convert_kreplanner(ind = 'domain-krep.pddl', inp = 'problem-krep.pddl', outd = 'out-dom.pddl', outp = 'out-prob.pddl'):
    
    # Do the initial conversion
    print("Running the following command...")
    krep_string = os.path.abspath('../prp-scripts/external/k-replanner') + " --options=kp:print:preprocessed --keep-intermediate-files --max-time 10 %s %s" % (ind, inp)
    print(krep_string)
    run_command(krep_string, MEMLIMIT=MEMLIMIT, TIMELIMIT=TIMELIMIT)
    print()
    
    domain_lines = get_lines('OUT', 'START_DOMAIN', 'END_DOMAIN')
    problem_lines = get_lines('OUT', 'START_PROBLEM', 'END_PROBLEM')
    
    # Convert the observation actions
    print("Converting observations to non-deterministic actions...")
    
    for i in range(len(domain_lines)):
        if '(:action sensor' in domain_lines[i]:
            if 'ver0' == domain_lines[i][-4:]:
                domain_lines[i] = domain_lines[i][:-5] + '_DETDUP_0'
            elif 'ver1' == domain_lines[i][-4:]:
                domain_lines[i] = domain_lines[i][:-5] + '_DETDUP_1'
            else:
                assert False, "Error with observation action: %s" % domain_lines[i]
    
    # Write output and clean up
    print("Writing new domain / problem and cleaning up...")
    write_file(outd, domain_lines)
    write_file(outp, problem_lines)
    os.system("rm OUT*")
    print()


def check_input(ind, inp):
    
    lines = read_file(ind)
    for line in lines:
        for word in bad_strings:
            if word in line.upper():
                print()
                print("Warning: Input contains the forbidden word %s" % word)
                print(line)
    print()
                

if __name__ == '__main__':
    myargs, flags = get_opts()
    
    print()
    
    if 2 != len(flags):
        print(USAGE_STRING)
        os._exit(1)
    
    if 'cf2cs' == flags[1]:
        convert = convert_cf2cs
    elif 'kreplanner' == flags[1]:
        convert = convert_kreplanner
    else:
        print("Invalid converter: %s" % flags[0])
        print(USAGE_STRING)
        os._exit(1)
    
    if 0 == len(myargs):
        convert()
    elif set(['-ind', '-inp', '-outd', '-outp']) - set(myargs.keys()):
        print(USAGE_STRING)
        os._exit(1)
    else:
        convert(myargs['-ind'], myargs['-inp'], myargs['-outd'], myargs['-outp'])
