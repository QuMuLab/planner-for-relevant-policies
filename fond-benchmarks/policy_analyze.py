
from krrt.utils import get_opts, match_value, get_value, load_CSV, write_file, append_file, read_file

import os, time

USAGE_STRING = """
Usage: python policy_analyze.py <TASK> -domain <domain> ...

        Where <TASK> may be:
          fip-vs-prp: Run a comparison between fip and the best setting for PRP
        """

BASEDIR = os.path.abspath(os.path.curdir)

def compare(domain):
    if 'all' == domain:
        for dom in GOOD_DOMAINS:
            compare(dom)
        return
    
    # Load both sets
    fip_data = load_CSV("RESULTS/fip-%s-results.csv" % domain)
    prp_data = load_CSV("RESULTS/prp-%s-results.csv" % domain)
    
    compare_data = ['domain,problem,fip time,prp time,fip size,prp size']
    
    assert len(fip_data) == len(prp_data)
    
    for i in range(len(fip_data)):
        assert (fip_data[i][0] == prp_data[i][0]) and (fip_data[i][1] == prp_data[i][1])
        compare_data.append("%s,%s,%s,%s,%s,%s" % (fip_data[i][0], fip_data[i][1],
                                                   fip_data[i][2], prp_data[i][2],
                                                   fip_data[i][3], prp_data[i][3]))
    
    write_file("RESULTS/%s-results.csv" % domain, compare_data)


if __name__ == '__main__':
    myargs, flags = get_opts()
    
    if '-domain' not in myargs:
        print "Error: Must choose a domain:"
        print USAGE_STRING
        os._exit(1)
    
    if 'fip-vs-prp' in flags:
        compare(myargs['-domain'])
