__author__ = 'manasvi'
from Tools.valgrind import Valgrind
from Tools.valgrind_rv import ValgrindRV
from Tools.compcert_rv import CompcertRV
from Tools.ub_san_rv import UBSanRV
from Tools.frama_c_rv import FramaCRV
from tabulate import tabulate
import sys


def merge(dict1, dict2):
    retdict = {}
    for key in dict1.keys():
        if key in dict2:
            retdict[key] = {"TP": set(dict1[key]["TP"]) | set(dict2[key]["TP"]),
                            "FP": set(dict1[key]["FP"]) | set(dict2[key]["FP"])}
        else:
            retdict[key] = dict1[key]

    for key in dict2.keys():
        if key not in dict1:
            retdict[key] = dict2[key]

    return retdict


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Needed: Path to Benchmark as arguments"
    else:
        path = sys.argv[1]
        tools = [UBSanRV(path), FramaCRV(path)]
        map(lambda x: x.run(), tools)
        numbers = []
        map(lambda x: numbers.append([x.get_tool_name(), x.get_numbers()["TP"], x.get_numbers()["FP"]]), tools)
        error_codes = reduce(lambda x, y: merge(x, y), map(lambda z: z.get_errors(), tools))
        print numbers
        print error_codes



