__author__ = 'manasvi'

from Tools.rv_benchmark.frama_c_rv import FramaCRV
from Tools.rv_benchmark.ub_san_rv import UBSanRV
from Tools.rv_benchmark.compcert_rv import CompcertRV
from Tools.rv_benchmark.valgrind_rv import ValgrindRV
from Tools.itc_benchmark.valgrind import Valgrind
from tabulate import tabulate
import sys


def tabulate_number_data(number_table):
    print tabulate(number_table, headers=["Tool", "% True Positives", "% False Positives"],
             tablefmt="latex")



def tabulate_error_codes(error_code_dict):
    error_code_arr = []
    for code in error_code_dict:
        row = [code, ", ".join(error_code_dict[code]["TP"]), ", ".join(error_code_dict[code]["FP"])]
        error_code_arr.append(row)
    print tabulate(error_code_arr, headers=["Error-Code", "True Positive Reported By", "False Positive Reported By"], tablefmt="latex")

def merge(dict1, dict2):
    retdict = {}
    for key in dict1.keys():
        if key not in retdict:
            retdict[key] = {"TP": set([]), "FP": set([])}

        retdict[key]["TP"] = retdict[key]["TP"] | dict1[key]["TP"]
        retdict[key]["FP"] = retdict[key]["FP"] | dict1[key]["FP"]

        if key in dict2:
            retdict[key]["TP"] = retdict[key]["TP"] | dict2[key]["TP"]
            retdict[key]["FP"] = retdict[key]["FP"] | dict2[key]["FP"]

    for key in dict2:
        if key not in retdict:
            retdict[key] = {"TP": dict2[key]["TP"],
                            "FP": dict2[key]["FP"]}

    return retdict


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Needed: Path to Benchmark as arguments"
    else:
        path = sys.argv[1]
        if sys.argv[2] == "rv":
            tools = [CompcertRV(path), ValgrindRV(path), FramaCRV(path), UBSanRV(path)]
            map(lambda x: x.run(), tools)
            numbers = []
            map(lambda x: numbers.append([x.get_tool_name(), x.get_numbers()["TP"], x.get_numbers()["FP"]]), tools)
            error_codes = reduce(lambda x, y: merge(x, y), map(lambda z: z.get_errors(), tools))
            tabulate_number_data(numbers)
            tabulate_error_codes(error_codes)
        if sys.argv[2] == "itc":
            print path
            tools = [CompcertRV(path)]
            map(lambda x: x.run(), tools)
