__author__ = 'manasvi'
from Tools.valgrind import Valgrind
from Tools.valgrind_rv import ValgrindRV
from Tools.compcert_rv import CompcertRV
from Tools.ub_san_rv import UBSanRV
from Tools.frama_c_rv import FramaCRV
from tabulate import tabulate
import sys

if __name__ == '__main__':
    # valgrind = Valgrind("~/Documents/itc-benchmarks/", "utils.csv")
    # valgrind.init()
    # valgrind.run()
    if len(sys.argv) < 2:
        print "Needed: Path to Benchmark as arguments"
    else:
        # valgrind = ValgrindRV(sys.argv[1])
        # valgrind.analyze()
        # compcert = CompcertRV(sys.argv[1])
        # compcert.analyze()
        # ubsan = UBSanRV(sys.argv[1])
        # ubsan.analyze()
        path = sys.argv[1]
        tools = [ValgrindRV(path)]
        # run the tools
        tools = map(lambda x: x.run(), tools)
        numbers = []
        map(lambda x: numbers.append([x.get_tool_name, x.get_numbers["TP"], x.get_numbers["FP"]]), tools)
        error_codes = reduce(lambda x, y: merge(x, y), map(lambda z: z.get_errors()), tools, {"TP": set("a"), "FP": set("b")})
        print numbers
        print error_codes


def merge(dict1, dict2):
    retdict = {}
    for key in dict1.keys():
        retdict[key] = {"TP": set(dict1[key]["TP"].items(), dict2[key]["TP"].items()),
                        "FP": set(dict1[key]["FP"].items(), dict2[key]["FP"].items())}
    return retdict
