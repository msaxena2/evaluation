__author__ = 'manasvi'
from Tools.valgrind import Valgrind


if __name__ == '__main__':
    valgrind = Valgrind("~/itc-benchmarks/", "utils.csv")
    valgrind.init()

