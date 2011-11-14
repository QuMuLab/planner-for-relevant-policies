
from krrt.utils import get_opts, match_value, get_value, load_CSV, write_file, append_file, read_file
from krrt.stats.plots import plot, create_time_profile
from krrt.stats import anova

from domains import GOOD_DOMAINS, FOND_DOMAINS

import os, time

USAGE_STRING = """
Usage: python policy_analyze.py <TASK> -domain <domain> ...

        Where <TASK> may be:
          fip-vs-prp: Run a comparison between fip and the best setting for prp
          prpga-vs-prp: Run a comparison between the best setting for prp, and the same settings with goal alternative
          pfip-vs-prp: Run a comparison between fip settings of prp, and the best setting for prp
          pfip-vs-psr: Run a comparison between fip settings of prp, and fip settings without goal alternative
          pfip-vs-pga: Run a comparison between fip settings of prp, and fip settings without state reuse
          pfip-vs-pbasic: Run a comparison between fip settings of prp, and fip settings without state reuse or goal alternative
          anova-time: Run an anova analysis of the parameters for prp, with time as the dependent variable
          anova-size: Run an anova analysis of the parameters for prp, with size as the dependent variable
        """

BASEDIR = os.path.abspath(os.path.curdir)

def filter_prp_settings(data, jiclimit, forgetpolicy, fullstate, planlocal, usepolicy):
    return filter(lambda x: x[5] == jiclimit and \
                            x[6] == forgetpolicy and \
                            x[7] == fullstate and \
                            x[8] == planlocal and \
                            x[9] == usepolicy,
                    data)

def average_prp_data(data):
    new_data = []
    mapping = {}
    for line in data:
        key = (line[0], line[1])
        if key in mapping:
            mapping[key].append(line)
        else:
            mapping[key] = [line]
    
    for (dom,prob) in mapping.keys():
        new_data.append([dom,prob])
        for i in range(2,len(data[0])):
            if i in [4, len(data[0]) - 2]:
                assert 1 == len(set([item[i] for item in mapping[(dom,prob)]]))
                new_data[-1].append(mapping[(dom,prob)][0][i])
            else:
                # Mean
                #new_data[-1].append(str(sum([float(item[i]) for item in mapping[(dom,prob)]], 0.0) / float(len(mapping[(dom,prob)]))))
                
                # Median
                new_data[-1].append(str(sorted([float(item[i]) for item in mapping[(dom,prob)]])[int(len(mapping[(dom,prob)])/2)]))
    
    return new_data

def print_setting(s):
    print "jic-limit(%s), forgetpolicy(%s), fullstate(%s), planlocal(%s), usepolicy(%s)" % (s[0], s[1], s[2], s[3], s[4])

def do_anova(domain, dep):
    if 'every' == domain:
        for dom in FOND_DOMAINS:
            do_anova(dom)
        return
    
    elif 'all' == domain:
        prp_data = []
        for dom in FOND_DOMAINS:
            prp_data.extend(load_CSV("RESULTS/prp-%s-results.csv" % dom))
    
    else:
        prp_data = load_CSV("RESULTS/prp-%s-results.csv" % domain)
    
    solved_prp_data = filter(lambda x: x[-2] == 'True', prp_data)
    
    anova([prp_data[0]] + solved_prp_data, ['fullstate','planlocal','usepolicy'], dependent = dep)

def prp_compare_two(domain, type1, type2, name1, name2):
    if 'every' == domain:
        for dom in FOND_DOMAINS:
            prp_compare_two(dom, type1, type2)
        return
    
    elif 'all' == domain:
        prp_data = []
        for dom in FOND_DOMAINS:
            prp_data.extend(load_CSV("RESULTS/prp-%s-results.csv" % dom))
    
    elif 'all-redundant' == domain:
        prp_data = []
        for i in range(1, 6):
            prp_data.extend(load_CSV("RESULTS/prp-blocksworld-redundant-%d-results.csv" % i))
    
    else:
        prp_data = load_CSV("RESULTS/prp-%s-results.csv" % domain)
    
    print "\nAnalyzing Two PRP Settings for %s:" % domain
    print_setting(type1)
    print_setting(type2)
    
    # Load both sets
    prp_data1 = [prp_data[0]] + filter_prp_settings(prp_data, *type1)
    solved_prp_data1 = filter(lambda x: x[-2] == 'True', prp_data1)
    solved_prp_data1 = average_prp_data(solved_prp_data1) # Filter and average based on what FIP has solved.
    
    prp_data2 = [prp_data[0]] + filter_prp_settings(prp_data, *type2)
    solved_prp_data2 = filter(lambda x: x[-2] == 'True', prp_data2)
    solved_prp_data2 = average_prp_data(solved_prp_data2) # Filter and average based on what FIP has solved.
    
    prp_mapping1 = {}
    prp_mapping2 = {}
    
    for line in solved_prp_data1:
        assert (line[0], line[1]) not in prp_mapping1
        prp_mapping1[(line[0], line[1])] = line
    
    for line in solved_prp_data2:
        assert (line[0], line[1]) not in prp_mapping2
        prp_mapping2[(line[0], line[1])] = line
    
    prp_solved1 = set(prp_mapping1.keys())
    prp_solved2 = set(prp_mapping2.keys())
    both_solved = prp_solved1 & prp_solved2
    
    print "%s Coverage: %d" % (name1, len(prp_solved1))
    print "%s Coverage: %d" % (name2, len(prp_solved2))
    print "Combined Coverage: %d" % len(both_solved)
    
    time_data = []
    size_data = []
    probs = []
    
    
    for (dom,prob) in both_solved:
        probs.append(prob)
        time_data.append((float(prp_mapping1[(dom,prob)][2]), float(prp_mapping2[(dom,prob)][2])))
        size_data.append((float(prp_mapping1[(dom,prob)][3]), float(prp_mapping2[(dom,prob)][3])))
    
    plot([item[0] for item in time_data], [item[1] for item in time_data],
         x_label = "%s Time (s)" % name1, y_label = "%s Time (s)" % name2, graph_name = "%s (Time)" % domain, makesquare = True, x_log = True, y_log = True)
    
    plot([item[0] for item in size_data], [item[1] for item in size_data],
         x_label = "%s Policy Size" % name1, y_label = "%s Policy Size" % name2, graph_name = "%s (Size)" % domain, makesquare = True, x_log = True, y_log = True)
    
    x1,y1 = create_time_profile([float(item[2]) for item in prp_mapping1.values()])
    x2,y2 = create_time_profile([float(item[2]) for item in prp_mapping2.values()])
    plot([x1,x2], [y1,y2], x_label = "Time (s)", y_label = "Problems Solved", no_scatter = True,
         xyline = False, legend_name = "Method", names = [name1, name2], x_log = True)
    
    print

def fip_vs_prp(domain):
    if 'every' == domain:
        for dom in FOND_DOMAINS:
            fip_vs_prp(dom)
        return
    
    elif 'all' == domain:
        fip_data = []
        prp_data = []
        for dom in FOND_DOMAINS:
            fip_data.extend(load_CSV("RESULTS/fip-%s-results.csv" % dom))
            prp_data.extend(load_CSV("RESULTS/prp-%s-results.csv" % dom))
    
    else:
        fip_data = load_CSV("RESULTS/fip-%s-results.csv" % domain)
        prp_data = load_CSV("RESULTS/prp-%s-results.csv" % domain)
    
    print "\nAnalyzing FIP vs PRP for %s:" % domain
    
    # Load both sets
    solved_fip_data = filter(lambda x: x[-1] == '-', fip_data)
    
    prp_data = [prp_data[0]] + filter_prp_settings(prp_data, '18000', '0', '0', '0', '1')
    solved_prp_data = filter(lambda x: x[-2] == 'True', prp_data)
    solved_prp_data = average_prp_data(solved_prp_data) # Filter and average based on what FIP has solved.
    
    fip_mapping = {}
    prp_mapping = {}
    
    for line in solved_fip_data:
        assert (line[0], line[1]) not in fip_mapping
        fip_mapping[(line[0], line[1])] = line
    
    for line in solved_prp_data:
        assert (line[0], line[1]) not in prp_mapping
        prp_mapping[(line[0], line[1])] = line
    
    fip_solved = set(fip_mapping.keys())
    prp_solved = set(prp_mapping.keys())
    both_solved = fip_solved & prp_solved
    
    print "FIP Coverage: %d" % len(fip_solved)
    print "PRP Coverage: %d" % len(prp_solved)
    print "Combined Coverage: %d" % len(both_solved)
    
    time_data = []
    size_data = []
    probs = []
    
    
    for (dom,prob) in both_solved:
        probs.append(prob)
        time_data.append((float(fip_mapping[(dom,prob)][2]), float(prp_mapping[(dom,prob)][2])))
        size_data.append((float(fip_mapping[(dom,prob)][3]), float(prp_mapping[(dom,prob)][3])))
    
    #HACK: We assign 0.001 seconds to a reported time of 0: This is needed for log plots to work
    
    plot([max(0.001, item[0]) for item in time_data], [max(0.001, item[1]) for item in time_data],
         x_label = "FIP Time (s)", y_label = "PRP Time (s)", graph_name = "FIP -vs- PRP: %s (Time)" % domain, makesquare = True, x_log = True, y_log = True)
    
    plot([item[0] for item in size_data], [item[1] for item in size_data],
         x_label = "FIP Policy Size", y_label = "PRP Policy Size", graph_name = "FIP -vs- PRP: %s (Size)" % domain, makesquare = True, x_log = True, y_log = True)
    
    x1,y1 = create_time_profile([item[0] for item in time_data])
    x2,y2 = create_time_profile([item[1] for item in time_data])
    plot([x1,x2], [y1,y2], x_label = "Time", y_label = "Problems Solved", no_scatter = True,
         xyline = False, legend_name = "Method", names = ["FIP", "PRP"], x_log = True)
    
    print


if __name__ == '__main__':
    myargs, flags = get_opts()
    
    if '-domain' not in myargs:
        print "Error: Must choose a domain:"
        print USAGE_STRING
        os._exit(1)
    
    if 'fip-vs-prp' in flags:
        fip_vs_prp(myargs['-domain'])
    
    if 'pfip-vs-prp' in flags:
        prp_compare_two(myargs['-domain'], ('18000', '0', '1', '1', '1'), ('18000', '0', '0', '0', '1'), 'PFIP', 'PRP')
    
    if 'pfip-vs-psr' in flags:
        prp_compare_two(myargs['-domain'], ('18000', '0', '1', '1', '1'), ('18000', '0', '1', '0', '1'), 'PFIP', 'PSR')
    
    if 'pfip-vs-pga' in flags:
        prp_compare_two(myargs['-domain'], ('18000', '0', '1', '1', '1'), ('18000', '0', '1', '1', '0'), 'PFIP', 'PGA')
    
    if 'pfip-vs-pbasic' in flags:
        prp_compare_two(myargs['-domain'], ('18000', '0', '1', '1', '1'), ('18000', '0', '1', '0', '0'), 'PFIP', 'PBASIC')
    
    if 'prpga-vs-prp' in flags:
        prp_compare_two(myargs['-domain'], ('18000', '0', '0', '1', '1'), ('18000', '0', '0', '0', '1'), 'PRP+GA', 'PRP')
    
    if 'anova-time' in flags:
        do_anova(myargs['-domain'], 'runtime')
    
    if 'anova-size' in flags:
        do_anova(myargs['-domain'], 'size')
