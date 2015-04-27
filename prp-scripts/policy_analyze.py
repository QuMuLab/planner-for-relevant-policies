
from krrt.utils import get_opts, match_value, get_value, load_CSV, write_file, append_file, read_file, get_file_list
from krrt.stats.plots import plot, create_time_profile
from krrt.stats import anova

from domains import GOOD_DOMAINS, FOND_DOMAINS, IPC06_DOMAINS, NEW_DOMAINS, INTERESTING_DOMAINS

import os, time

USAGE_STRING = """
Usage: python policy_analyze.py <TASK> -domain <domain> ...

        Where <TASK> may be:
          fip-vs-prp: Run a comparison between fip and the best setting for prp
          pfip-vs-prp: Run a comparison between fip settings of prp, and the best setting for prp
          prp: Run a comparison with the best prp settings and itself (just used to get prp stats)
          ffreplan-vs-prp: Run a comparison between ffreplan, and prp in online replanning
          anova-time: Run an anova analysis of the parameters for prp, with time as the dependent variable
          anova-size: Run an anova analysis of the parameters for prp, with size as the dependent variable
          ablation: Run the ablation comparisons (optimal settings vs disabling some feature)
          ab-compare: Run a comparison between two results directories (use -res1 and -res2 as parameters)
        """

BASEDIR = os.path.abspath(os.path.curdir)

def filter_prp_settings(data,
                        jiclimit,
                        forgetpolicy,
                        fullstate,
                        planlocal,
                        partial_planlocal,
                        use_policy,
                        limit_planlocal,
                        detect_deadends,
                        generalize_deadends,
                        online_deadends,
                        optimized_scd):

    return filter(lambda x: x[5] == jiclimit and \
                            x[7] == forgetpolicy and \
                            x[8] == fullstate and \
                            x[9] == planlocal and \
                            x[10] == partial_planlocal and \
                            x[11] == use_policy and \
                            x[12] == limit_planlocal and \
                            x[13] == detect_deadends and \
                            x[14] == generalize_deadends and \
                            x[15] == online_deadends and \
                            x[16] == optimized_scd,
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
                if mapping[(dom,prob)][0][i] == '-':
                    new_data[-1].append('-')
                else:
                    new_data[-1].append(str(sorted([float(item[i]) for item in mapping[(dom,prob)]])[int(len(mapping[(dom,prob)])/2)]))

    return new_data

def print_setting(s):
    print "jic-limit(%s), forgetpolicy(%s), fullstate(%s),\
           \nplanlocal(%s), partial-planloca(%s), usepolicy(%s),\
           \nlimit-planlocal(%s), detect-deadends(%s), generalize-deadends(%s),\
           \nonline-deadends(%s), optimized-scd(%s)" % (s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8], s[9], s[10])

def do_anova(domain, dep):
    if 'every' == domain:
        for dom in FOND_DOMAINS:
            do_anova(dom)
        return

    elif 'all' in domain:
        prp_data = []
        dom_type = []
        if 'fond' in domain:
            dom_type = FOND_DOMAINS
        elif 'new' in domain:
            dom_type = NEW_DOMAINS
        elif 'ipc' in domain:
            dom_type = IPC06_DOMAINS
        elif 'interesting' in domain:
            dom_type = INTERESTING_DOMAINS

        for dom in dom_type:
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

    elif ('all' in domain) and ('redundant' not in domain):
        prp_data = []
        dom_type = []
        if 'fond' in domain:
            dom_type = FOND_DOMAINS
        elif 'new' in domain:
            dom_type = NEW_DOMAINS
        elif 'ipc' in domain:
            dom_type = IPC06_DOMAINS
        elif 'interesting' in domain:
            dom_type = INTERESTING_DOMAINS

        for dom in dom_type:
            prp_data.extend(load_CSV("RESULTS/prp-%s-results.csv" % dom))

    elif 'all-redundant' == domain:
        prp_data = []
        for i in range(1, 6):
            prp_data.extend(load_CSV("RESULTS/prp-blocksworld-redundant-%d-results.csv" % i))

    else:
        prp_data = load_CSV("RESULTS/prp-%s-results.csv" % domain)

    return _prp_compare_two(domain, type1, type2, name1, name2, prp_data)

def _prp_compare_two(domain, type1, type2, name1, name2, prp_data):
    print "\nAnalyzing Two PRP Settings for %s:" % domain
    print_setting(type1)
    print "\n  -vs-\n"
    print_setting(type2)
    print

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

    print "%s Avg time: %f" % (name1, sum([item[0] for item in time_data]) / float(len(time_data)))
    print "%s Avg time: %f" % (name2, sum([item[1] for item in time_data]) / float(len(time_data)))
    print "%s Total time: %f" % (name1, sum([item[0] for item in time_data]))
    print "%s Total time: %f" % (name2, sum([item[1] for item in time_data]))
    print "%s Avg size: %f" % (name1, sum([item[0] for item in size_data]) / float(len(size_data)))
    print "%s Avg size: %f" % (name2, sum([item[1] for item in size_data]) / float(len(size_data)))

    if name1 == name2:
        return

    plot([item[0] for item in time_data], [item[1] for item in time_data],
         x_label = "%s Time (s)" % name1, y_label = "%s Time (s)" % name2, makesquare = True, x_log = True, y_log = True, col = False)

    plot([item[0] for item in size_data], [item[1] for item in size_data],
         x_label = "%s Policy Size" % name1, y_label = "%s Policy Size" % name2, makesquare = True, x_log = True, y_log = True, col = False)

    x1,y1 = create_time_profile([float(item[2]) for item in prp_mapping1.values()])
    x2,y2 = create_time_profile([float(item[2]) for item in prp_mapping2.values()])
    plot([x1,x2], [y1,y2], x_label = "Time (s)", y_label = "Problems Solved", no_scatter = True,
         xyline = False, names = [name1, name2], x_log = True, col = False)

    print

def fip_vs_prp(domain):
    if 'every' in domain:
        dom_type = []
        if 'fond' in domain:
            dom_type = FOND_DOMAINS
        elif 'new' in domain:
            dom_type = NEW_DOMAINS
        elif 'ipc' in domain:
            dom_type = IPC06_DOMAINS
        elif 'interesting' in domain:
            dom_type = INTERESTING_DOMAINS

        for dom in dom_type:
            fip_vs_prp(dom)
        return

    elif 'all' in domain:
        fip_data = []
        prp_data = []
        dom_type = []
        if 'fond' in domain:
            dom_type = FOND_DOMAINS
        elif 'new' in domain:
            dom_type = NEW_DOMAINS
        elif 'ipc' in domain:
            dom_type = IPC06_DOMAINS
        elif 'interesting' in domain:
            dom_type = INTERESTING_DOMAINS

        for dom in dom_type:
            prp_data.extend(load_CSV("RESULTS/prp-%s-results.csv" % dom))

        fip_data = []
        prp_data = []
        for dom in dom_type:
            fip_data.extend(load_CSV("RESULTS/fip-%s-results.csv" % dom))
            prp_data.extend(load_CSV("RESULTS/prp-%s-results.csv" % dom))

    else:
        fip_data = load_CSV("RESULTS/fip-%s-results.csv" % domain)
        prp_data = load_CSV("RESULTS/prp-%s-results.csv" % domain)

    print "\nAnalyzing FIP vs PRP for %s:" % domain

    # Load both sets
    solved_fip_data = filter(lambda x: x[-1] == '-' and x[-2] != '0', fip_data)
    nosol_fip_data = filter(lambda x: x[-1] == 'N', fip_data)

    prp_data = [prp_data[0]] + filter_prp_settings(prp_data, '18000', '0', '0', '1', '1', '1', '1', '1', '1', '1', '1')
    solved_prp_data = filter(lambda x: x[-2] == 'True', prp_data)
    solved_prp_data = average_prp_data(solved_prp_data)
    nosol_prp_data = filter(lambda x: x[4] == 'N' or x[-2] == 'False', prp_data)
    nosol_prp_data = average_prp_data(nosol_prp_data)

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

    print "FIP Coverage: %d / %d" % (len(fip_solved), len(nosol_fip_data))
    print "PRP Coverage: %d / %d" % (len(prp_solved), len(nosol_prp_data))
    print "Combined Coverage: %d" % len(both_solved)
    print "FIP - PRP: %s" % str(fip_solved - prp_solved)

    all_time_data = []
    time_data = []
    size_data = []
    probs = []


    for (dom,prob) in both_solved:
        probs.append(prob)
        time_data.append((float(fip_mapping[(dom,prob)][2]), float(prp_mapping[(dom,prob)][17])))
        size_data.append((float(fip_mapping[(dom,prob)][3]), float(prp_mapping[(dom,prob)][3])))

    #HACK: We assign 0.001 seconds to a reported time of 0: This is needed for log plots to work

    plot([max(0.001, item[0]) for item in time_data], [max(0.001, item[1]) for item in time_data],
         x_label = "FIP Time (s)", y_label = "PRP Time (s)", makesquare = True, x_log = True, y_log = True, col = False)

    plot([item[0] for item in size_data], [item[1] for item in size_data],
         x_label = "FIP Policy Size", y_label = "PRP Policy Size", makesquare = True, x_log = True, y_log = True, col = False)

    x1,y1 = create_time_profile([max(0.001, float(fip_mapping[(dom,prob)][2])) for (dom,prob) in fip_solved])
    x2,y2 = create_time_profile([max(0.001, float(prp_mapping[(dom,prob)][17])) for (dom,prob) in prp_solved])

    plot([x1,x2], [y1,y2], x_label = "Time", y_label = "Problems Solved", no_scatter = True,
         xyline = False, names = ["FIP", "PRP"], x_log = True, col = False)

    print


def online_compare(domain):
    if 'every' in domain:
        dom_type = []
        if 'fond' in domain:
            dom_type = FOND_DOMAINS
        elif 'new' in domain:
            dom_type = NEW_DOMAINS
        elif 'ipc' in domain:
            dom_type = IPC06_DOMAINS
        elif 'interesting' in domain:
            dom_type = INTERESTING_DOMAINS

        for dom in dom_type:
            online_compare(dom)
        return

    elif 'all' in domain:
        prp_data = []
        ffr_data = []
        dom_type = []
        if 'fond' in domain:
            dom_type = FOND_DOMAINS
        elif 'new' in domain:
            dom_type = NEW_DOMAINS
        elif 'ipc' in domain:
            dom_type = IPC06_DOMAINS
        elif 'interesting' in domain:
            dom_type = INTERESTING_DOMAINS

        for dom in dom_type:
            prp_data.extend(load_CSV("RESULTS/bo-prp-%s-results.csv" % dom))
            ffr_data.extend(load_CSV("RESULTS/ffr-prp-%s-results.csv" % dom))

    else:
        prp_data = load_CSV("RESULTS/bo-prp-%s-results.csv" % domain)
        ffr_data = load_CSV("RESULTS/ffr-prp-%s-results.csv" % domain)

    # Load both sets
    solved_prp_data = filter(lambda x: x[4] == '-', prp_data)
    solved_ffr_data = filter(lambda x: x[4] == '-', ffr_data)

    prp_mapping = {}
    ffr_mapping = {}

    for line in solved_ffr_data:
        assert (line[0], line[1]) not in ffr_mapping
        ffr_mapping[(line[0], line[1])] = line

    for line in solved_prp_data:
        assert (line[0], line[1]) not in prp_mapping
        prp_mapping[(line[0], line[1])] = line

    ffr_solved = set(ffr_mapping.keys())
    prp_solved = set(prp_mapping.keys())
    both_solved = ffr_solved & prp_solved

    ffr_actions = []
    prp_actions = []
    ffr_replans = []
    prp_replans = []
    ffr_times = []
    prp_times = []
    ffr_success = []
    prp_success = []

    for (dom,prob) in both_solved:
        ffr_actions.append(float(ffr_mapping[(dom,prob)][-4]))
        prp_actions.append(float(prp_mapping[(dom,prob)][-4]))
        ffr_replans.append(float(ffr_mapping[(dom,prob)][-5]))
        prp_replans.append(float(prp_mapping[(dom,prob)][-5]))
        ffr_success.append(float(ffr_mapping[(dom,prob)][-1]))
        prp_success.append(float(prp_mapping[(dom,prob)][-1]))
        ffr_times.append(float(ffr_mapping[(dom,prob)][-7]) / float(ffr_mapping[(dom,prob)][6]))
        prp_times.append(float(prp_mapping[(dom,prob)][-7]) / float(prp_mapping[(dom,prob)][6]))

    print "Online replanning for domain %s:\n" % domain
    print "Total ffr successful runs: %d" % len(ffr_solved)
    print "Total prp successful runs: %d" % len(prp_solved)
    print "Total shared successful runs: %d\n" % len(both_solved)
    print "FFR Average Actions: %f" % (sum(ffr_actions) / float(len(ffr_actions)))
    print "PRP Average Actions: %f\n" % (sum(prp_actions) / float(len(prp_actions)))
    print "FFR Average Replans: %f" % (sum(ffr_replans) / float(len(ffr_replans)))
    print "PRP Average Replans: %f\n" % (sum(prp_replans) / float(len(prp_replans)))
    print "FFR Average Success: %f" % (sum(ffr_success) / float(len(ffr_success)))
    print "PRP Average Success: %f\n" % (sum(prp_success) / float(len(prp_success)))
    print "FFR Total Success: %d" % int(sum(ffr_success))
    print "PRP Total Success: %d\n" % int(sum(prp_success))
    print "FFR Average Time: %f" % (sum(ffr_times) / float(len(ffr_times)))
    print "PRP Average Time: %f\n" % (sum(prp_times) / float(len(prp_times)))
    return


def ab_compare(res1, res2):

    def get_time(line):
        if line[4] == '-':
            return max(0.1,float(line[2]))
        else:
            return float('inf')

    def get_size(line):
        if line[4] == '-':
            return float(line[3])
        else:
            return float('inf')

    def get_score(_x, y):
        x = max(_x, 0.001)
        if x == float('inf') and y == float('inf'):
            return 0.0
        else:
            return min(x,y) / x

    res1_experiments = set(map(lambda x: x.split('/')[-1], get_file_list(res1, match_list=['.csv'])))
    res2_experiments = set(map(lambda x: x.split('/')[-1], get_file_list(res2, match_list=['.csv'])))
    shared_results = list(res1_experiments & res2_experiments)

    print
    print "Found %d overlapping experiments to compare." % len(shared_results)

    time_score = [0.0, 0.0]
    size_score = [0.0, 0.0]
    coverage   = [0,0]

    for res in shared_results:
        data1 = load_CSV(res1+'/'+res)[1:]
        data2 = load_CSV(res2+'/'+res)[1:]

        if len(data1) != len(data2):
            print "Error with %s experiment -- different number of data points." % res
            continue

        times1 = [get_time(line) for line in data1]
        times2 = [get_time(line) for line in data2]
        time1 = sum([get_score(times1[i], times2[i]) for i in range(len(data1))])
        time2 = sum([get_score(times2[i], times1[i]) for i in range(len(data1))])

        sizes1 = [get_size(line) for line in data1]
        sizes2 = [get_size(line) for line in data2]
        size1 = sum([get_score(sizes1[i], sizes2[i]) for i in range(len(data1))])
        size2 = sum([get_score(sizes2[i], sizes1[i]) for i in range(len(data1))])

        cov1 = len(filter(lambda x: x[4] == '-', data1))
        cov2 = len(filter(lambda x: x[4] == '-', data2))

        time_score[0] += time1
        time_score[1] += time2
        size_score[0] += size1
        size_score[1] += size2
        coverage[0] += cov1
        coverage[1] += cov2

        print "\n    [ %s ]\n" % res.split('-results.csv')[0]
        print "  Coverage: %d -vs- %d" % (cov1, cov2)
        print "Size Score: %.2f -vs- %.2f" % (size1, size2)
        print "Time Score: %.2f -vs- %.2f\n" % (time1, time2)

    print "\n    [ OVERALL ]"
    print "  Coverage: %d -vs- %d" % (coverage[0], coverage[1])
    print "Size Score: %.2f -vs- %.2f" % (size_score[0], size_score[1])
    print "Time Score: %.2f -vs- %.2f" % (time_score[0], time_score[1])
    print


if __name__ == '__main__':
    myargs, flags = get_opts()

    if 'ab-compare' in flags:
        if '-res1' not in myargs or '-res2' not in myargs:
            print "Error: Must specify two result directories:"
            print USAGE_STRING
            os._exit(1)
        ab_compare(myargs['-res1'], myargs['-res2'])
        os._exit(1)

    if '-domain' not in myargs:
        print "Error: Must choose a domain:"
        print USAGE_STRING
        os._exit(1)

    if 'fip-vs-prp' in flags:
        fip_vs_prp(myargs['-domain'])

    if 'prp' in flags:
        prp_compare_two(myargs['-domain'],
                        ('18000', '0', '0', '1', '1', '1', '1', '1', '1', '1', '1'),
                        ('18000', '0', '0', '1', '1', '1', '1', '1', '1', '1', '1'),
                        'PRP', 'PRP')

    if 'pfip-vs-prp' in flags:
        prp_compare_two(myargs['-domain'],
                        ('18000', '0', '1', '1', '0', '1', '0', '0', '0', '0', '0'),
                        ('18000', '0', '0', '1', '0', '1', '0', '0', '0', '0', '0'),
                        'PRP$_{\\textrm{Full}}$', 'PRP')

    if 'ffreplan-vs-prp' in flags:
        online_compare(myargs['-domain'])

    if 'anova-time' in flags:
        do_anova(myargs['-domain'], 'runtime')

    if 'anova-size' in flags:
        do_anova(myargs['-domain'], 'size')

    if 'ablation' in flags:

        prp_data = load_CSV("RESULTS/best-prp-%s-results.csv" % myargs['-domain']) + \
                   load_CSV("RESULTS/no-local-prp-%s-results.csv" % myargs['-domain'])
        _prp_compare_two(myargs['-domain'],
                        ('18000', '0', '0', '1', '1', '1', '1', '1', '1', '1', '1'),
                        ('18000', '0', '0', '1', '0', '1', '0', '1', '1', '1', '1'),
                        'PRP', 'PRP$_{\\textrm{-local}}$', prp_data)

        prp_data = load_CSV("RESULTS/best-prp-%s-results.csv" % myargs['-domain']) + \
                   load_CSV("RESULTS/no-scd-prp-%s-results.csv" % myargs['-domain'])
        _prp_compare_two(myargs['-domain'],
                        ('18000', '0', '0', '1', '1', '1', '1', '1', '1', '1', '1'),
                        ('18000', '0', '0', '1', '1', '1', '1', '1', '1', '1', '0'),
                        'PRP', 'PRP$_{\\textrm{-scd}}$', prp_data)

        prp_data = load_CSV("RESULTS/best-prp-%s-results.csv" % myargs['-domain']) + \
                   load_CSV("RESULTS/no-deadend-prp-%s-results.csv" % myargs['-domain'])
        _prp_compare_two(myargs['-domain'],
                        ('18000', '0', '0', '1', '1', '1', '1', '1', '1', '1', '1'),
                        ('18000', '0', '0', '1', '1', '1', '1', '1', '0', '0', '1'),
                        'PRP', 'PRP$_{\\textrm{-deadend}}$', prp_data)

        prp_data = load_CSV("RESULTS/best-prp-%s-results.csv" % myargs['-domain']) + \
                   load_CSV("RESULTS/no-partial-prp-%s-results.csv" % myargs['-domain'])
        _prp_compare_two(myargs['-domain'],
                        ('18000', '0', '0', '1', '1', '1', '1', '1', '1', '1', '1'),
                        ('18000', '0', '1', '1', '0', '1', '1', '1', '0', '1', '1'),
                        'PRP', 'PRP$_{\\textrm{-partial}}$', prp_data)
