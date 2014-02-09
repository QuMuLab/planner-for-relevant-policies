import sys
properties = ['expanded', 'total_time', 'solved']     

dict = {}
execfile(sys.argv[1], dict)
for prop in properties:    
    print 'BB_PROP', prop + "-" + dict['config'] + "-" + dict['domain'] + "-" + dict['problem'], dict[prop]                        