
import sys

num = int(sys.argv[1])

print "(define (problem p%d)" % num
print "    (:domain ctp)"
print "    "
print "    (:objects"
print "        %s - vertex" % ' '.join(["v%d" % i for i in range(num+1)])
print "        %s - edge)" % ' '.join(["e%d" % i for i in range(2*num)])
print "    (:init"
print "    "
for i in range(num):
    print "        (adjacent v%d e%d) (adjacent v%d e%d)" % (i, i*2, i+1, i*2)
    print "        (adjacent v%d e%d) (adjacent v%d e%d)" % (i, i*2+1, i+1, i*2+1)
    print "        "

print "        (at v0)"
print "        "

for i in range(num):
    print "        (oneof (traversable e%d) (traversable e%d))" % (i*2, i*2+1)

print "    )"
print "    "
print "    (:goal (at v%d))" % num
print ")"