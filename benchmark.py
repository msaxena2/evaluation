__author__ = 'manasvi'

from Tools.rv_benchmark.frama_c_rv import FramaCRV
from Tools.rv_benchmark.ub_san_rv import UBSanRV
from Tools.rv_benchmark.compcert_rv import CompcertRV
from Tools.rv_benchmark.valgrind_rv import ValgrindRV
from tabulate import tabulate
import sys


def tabulate_number_data(number_table):
    tabulate(number_table, headers=["Tool", "% True Positives", "% False Positives"],
                                    tablefmt="fancy_grid")


def tabulate_error_codes(error_code_dict):
    error_code_arr = ["Error-Code", "True Positive Reported By", "False Positive Reported By"]
    for code in error_code_dict.keys():
        row = [code, ", ".join(row[code]["TP"]), ", ".join(row[code]["FP"])]

def merge(dict1, dict2):
    retdict = {}
    for key in dict1.keys():
        if key not in retdict:
            retdict[key] = {"TP": set([]), "FP": set([])}

        retdict[key]["TP"] = retdict[key]["TP"] | dict1[key]["TP"]
        retdict[key]["TP"] = retdict[key]["FP"] | dict1[key]["FP"]
        if key in dict2:
            retdict[key]["TP"] = retdict[key]["TP"] | dict2[key]["TP"]
            retdict[key]["TP"] = retdict[key]["FP"] | dict2[key]["FP"]

    for key in dict2:
        if key not in retdict:
            retdict[key] = set([])
        if key not in dict1:
            retdict[key]["TP"] = retdict[key]["TP"] | dict2[key]["TP"]
            retdict[key]["TP"] = retdict[key]["FP"] | dict2[key]["FP"]

    return retdict


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Needed: Path to Benchmark as arguments"
    else:
        path = sys.argv[1]
        tools = [CompcertRV(path), ValgrindRV(path)]
        map(lambda x: x.run(), tools)
        numbers = []
        map(lambda x: numbers.append([x.get_tool_name(), x.get_numbers()["TP"], x.get_numbers()["FP"]]), tools)
        error_codes = reduce(lambda x, y: merge(x, y), map(lambda z: z.get_errors(), tools))
        tabulate_number_data(numbers)
        print error_codes

