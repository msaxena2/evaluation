__author__ = 'manasvi'
from Tools.valgrind import Valgrind
from Tools.valgrind_rv import ValgrindRV


if __name__ == '__main__':
    #valgrind = Valgrind("~/Documents/itc-benchmarks/", "utils.csv")
    #valgrind.init()
    #valgrind.run()
    valgrind = ValgrindRV("/Users/manasvi/Documents/c-semantics/examples/error-codes")
    valgrind.run()