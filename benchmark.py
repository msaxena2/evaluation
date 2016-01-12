__author__ = 'manasvi'
from Tools.valgrind import Valgrind
from Tools.valgrind_rv import ValgrindRV
import sys

if __name__ == '__main__':
    #valgrind = Valgrind("~/Documents/itc-benchmarks/", "utils.csv")
    #valgrind.init()
    #valgrind.run()
    if len(sys.argv) < 2:
        print "Needed: Path to Benchmark as arguments"
    else:
        valgrind = ValgrindRV(sys.argv[1])
        valgrind.analyze()