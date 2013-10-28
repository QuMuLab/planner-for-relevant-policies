from krrt.utils import read_file, get_opts
from krrt.stats.plots import plot, create_time_profile

good_domains = ['search-and-rescue', 'triangle-tireworld', 'miconic-simpleadl', 'schedule']
dom_names = ['search', 'tireworld', 'miconic', 'schedule']

if '-csv' in get_opts()[0]:
    data = [line.split(',') for line in read_file(get_opts()[0]['-csv'])[1:]]
    
    times = [float(i[0]) for i in data]
    sizes = [float(i[1]) for i in data]
    
    print "Mean time: %f" % (sum(times) / len(times))
    print "Mean size: %f" % (sum(sizes) / len(sizes))

else:
    times = []
    sizes = []
    xs = []
    for dom in good_domains:
        data = [line.split(',') for line in read_file("%s.csv" % dom)[1:]]
        times.append(sorted([float(i[0]) for i in data]))
        sizes.append(sorted([float(i[1]) for i in data]))
        xs.append([i+1 for i in range(len(data))])

    plot(x=xs,
         y=times,
         x_label="Problem",
         y_label="Runtime (s)",
         col=True,
         y_log=True,
         #names=dom_names,
         names=None,
         xyline=False,
         no_scatter=True)
    
    plot(x=xs,
        y=sizes,
        x_label="Problem",
        y_label="Policy Size",
        col=True,
        y_log=False,
        names=dom_names,
        xyline=False,
        no_scatter=True)

