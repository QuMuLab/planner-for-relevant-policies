from krrt.utils import read_file, get_opts

data = [line.split(',') for line in read_file(get_opts()[0]['-csv'])[1:]]

times = [float(i[0]) for i in data]
sizes = [float(i[1]) for i in data]

print "Mean time: %f" % (sum(times) / len(times))
print "Mean size: %f" % (sum(sizes) / len(sizes))

