from krrt.utils import read_file, get_opts
#from krrt.stats.plots import plot, create_time_profile

good_domains = ['search-and-rescue', 'triangle-tireworld', 'miconic-simpleadl', 'schedule']
dom_names = ['search', 'tireworld', 'miconic', 'schedule']

title_lookup = {
  'search-and-rescue': 'Search and Rescue',
  'miconic-simpleadl': 'Buggy Miconic',
  'schedule': 'Sloppy Schedule',
  'triangle-tireworld': 'Tedious Tireworld'
}

def get_figsize(fig_width_pt):
    import math
    inches_per_pt = 1.0/72.0                # Convert pt to inch
    golden_mean = (math.sqrt(5)-1.0)/2.0    # Aesthetic ratio
    fig_width = fig_width_pt*inches_per_pt  # width in inches
    fig_height = fig_width*golden_mean     # height in inches
    fig_size =  [fig_width,fig_height]      # exact figsize
    return fig_size

def individual_plot(xs, data, logplot, title):
    
    # Copied / modified from krrt
    import pylab
    pylab.rcParams.update({'backend': 'eps',
                    'legend.pad': 0.1,    # empty space around the legend box
                    'legend.fontsize': 11,
                    'lines.markersize': 3,
                    'font.size': 12,
                    'font.family': 'serif',
                    'ps.usedistiller': 'xpdf',
                    #'font.family': 'sans-serif',
                    'font.serif': 'Times New Roman',
                    #'font.sans-serif': 'Helvetica',
                    'text.usetex': True,
                    'figure.figsize': get_figsize(250)})
    
    f, (ax1) = pylab.subplots(1)
    
    SYMBOLS = ['s', 'x', 'o', '^', '>', 'v', '<', 'd', 'p', 'h', '8']
    COLOURS = ['b','g','k','m']
    LINES = ['-', '--', '-.', ':']
    
    handle = ax1.plot(xs, data, c='b', ls='-')
    
    ax1.set_title(title)
    
    if logplot:
        ax1.set_yscale('log')
    
    pylab.show()

if '-csv' in get_opts()[0]:
    data = [line.split(',') for line in read_file(get_opts()[0]['-csv'])[1:]]
    
    times = [float(i[0]) for i in data]
    sizes = [float(i[1]) for i in data]
    
    print "Mean time: %f" % (sum(times) / len(times))
    print "Mean size: %f" % (sum(sizes) / len(sizes))

elif '-size' in get_opts()[0]:
    dom = get_opts()[0]['-size']
    fname = "%s.csv" % dom
    data = [line.split(',') for line in read_file(fname)[1:]]
    times = sorted([float(i[0]) for i in data])
    sizes = sorted([float(i[1]) for i in data])
    xs = [i+1 for i in range(len(data))]
    individual_plot(xs, sizes, False, title_lookup[dom])

elif '-time' in get_opts()[0]:
    dom = get_opts()[0]['-time']
    fname = "%s.csv" % dom
    data = [line.split(',') for line in read_file(fname)[1:]]
    times = sorted([float(i[0]) for i in data])
    sizes = sorted([float(i[1]) for i in data])
    xs = [i+1 for i in range(len(data))]
    individual_plot(xs, times, True, title_lookup[dom])

else:
    
    times = []
    sizes = []
    xs = []
    for dom in good_domains:
        data = [line.split(',') for line in read_file("%s.csv" % dom)[1:]]
        times.append(sorted([float(i[0]) for i in data]))
        sizes.append(sorted([float(i[1]) for i in data]))
        xs.append([i+1 for i in range(len(data))])
    
    
    
    # Copied / modified from krrt
    import pylab
    pylab.rcParams.update({'backend': 'eps',
                    'legend.pad': 0.1,    # empty space around the legend box
                    'legend.fontsize': 11,
                    'lines.markersize': 3,
                    'font.size': 12,
                    'font.family': 'serif',
                    'ps.usedistiller': 'xpdf',
                    #'font.family': 'sans-serif',
                    'font.serif': 'Times New Roman',
                    #'font.sans-serif': 'Helvetica',
                    'text.usetex': True,
                    'figure.figsize': get_figsize(250)})
    
    #pylab.figure(1)
    #pylab.clf()
    
    f, (ax1, ax2) = pylab.subplots(2, sharex=True, sharey=False)
    
    SYMBOLS = ['s', 'x', 'o', '^', '>', 'v', '<', 'd', 'p', 'h', '8']
    COLOURS = ['b','g','k','m']
    LINES = ['-', '--', '-.', ':']
    LINES = ['-', '--', '-.', ':']
    
    handles1 = []
    handles2 = []
    
    for i in range(len(dom_names)):
        handles1.append(ax1.plot(xs[i], sizes[i], c=COLOURS[i], ls=LINES[i]))
        handles2.append(ax2.plot(xs[i], times[i], c=COLOURS[i], ls=LINES[i]))
        #handles1.append(ax1.scatter(xs[i], sizes[i], c=COLOURS[i], marker=SYMBOLS[i]))
        #handles2.append(ax2.scatter(xs[i], times[i], c=COLOURS[i], marker=SYMBOLS[i]))
    
    ax1.legend(dom_names, loc="upper left")
    
    #ax = pylab.axes([0.17,0.22,0.95-0.17,0.95-0.22])
    
    ax2.set_yscale('log')
    pylab.xlabel('Problem')
    
    ax1.set_ylabel('Policy Size')
    ax2.set_ylabel('Runtime (s)')
    
    ax1.xaxis.set_major_formatter( pylab.NullFormatter() )
    ax2.xaxis.set_major_formatter( pylab.NullFormatter() )
    
    #ax1.plot(x, y)
    #ax1.set_title('Sharing both axes')
    #ax2.scatter(x, y)
    #ax3.scatter(x, 2 * y ** 2 - 1, color='r')
    # Fine-tune figure; make subplots close to each other and hide x ticks for
    # all but bottom plot.
    f.subplots_adjust(hspace=0,left=0.2,top=0.95,right=0.96)
    pylab.setp([a.get_xticklabels() for a in f.axes[:-1]], visible=False)
    
    ax2.yaxis.get_major_ticks()[-1].label1.set_visible(False)
    
    
    pylab.show()
    
   #plot(x=xs,
         #y=times,
         #x_label="Problem",
         #y_label="Runtime (s)",
         #col=True,
         #y_log=True,
         ##names=dom_names,
         #names=None,
         #xyline=False,
         #no_scatter=True)
    
    #plot(x=xs,
        #y=sizes,
        #x_label="Problem",
        #y_label="Policy Size",
        #col=True,
        #y_log=False,
        #names=dom_names,
        #xyline=False,
        #no_scatter=True)

