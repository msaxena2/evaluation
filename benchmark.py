__author__ = 'manasvi'

from tools.rv_benchmark.frama_c_rv import FramaCRV
from tools.rv_benchmark.ub_san_rv import UBSanRV
from tools.rv_benchmark.compcert_rv import CompcertRV
from tools.rv_benchmark.valgrind_rv import ValgrindRV
from tools.itc_benchmark.valgrind import Valgrind
from tools.itc_benchmark.comcert import Compcert
from tools.itc_benchmark.ub_san import UBSan
from tools.itc_benchmark.rv_match import RVMatch
from tools.itc_benchmark.frama_c import FramaC
import math
import os
from tabulate import tabulate
import sys
from  utils.external_info import Info

info = Info()
error_info = info.get_spec_dict()
ignore_list = info.get_ignore_list()
ignore_dict = info.get_ignore_dict()


def tabulate_number_data(number_table):
    print tabulate(number_table, headers=["Tool", "% True Positives", "% False Positives"],
                   tablefmt="latex")


def tabulate_error_codes(error_code_dict):
    error_code_arr = []
    for code in error_code_dict:
        row = [code, ", ".join(error_code_dict[code]["TP"]), ", ".join(error_code_dict[code]["FP"])]
        error_code_arr.append(row)
    print tabulate(error_code_arr, headers=["Error-Code", "True Positive Reported By", "False Positive Reported By"],
                   tablefmt="latex")


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


def run_rv_benchmark(log_location):
    global tools, numbers
    tools = [CompcertRV(path), ValgrindRV(path), FramaCRV(path), UBSanRV(path)]
    map(lambda x: x.run(), tools)
    numbers = []
    map(lambda x: numbers.append([x.get_tool_name(), x.get_numbers()["TP"], x.get_numbers()["FP"]]), tools)
    error_codes = reduce(lambda x, y: merge(x, y), map(lambda z: z.get_errors(), tools))
    tabulate_number_data(numbers)
    tabulate_error_codes(error_codes)


def crunch_data(output_dict):
    return_dict = {}
    for key in output_dict:
        return_key = error_info[key]["type"]
        if return_key not in return_dict:
            return_dict[return_key] = {"count": 0, "TP": 0,
                                       "FP": 0}

        return_dict[return_key]["count"] += output_dict[key]["count"]
        return_dict[return_key]["TP"] += output_dict[key]["TP"]
        return_dict[return_key]["FP"] += output_dict[key]["FP"]

    return return_dict


def tabulate_itc_criteria(tool_list, crunched_data):
    header = [" "]
    for tool in tool_list:
        header.append(tool + " (DR)")
        header.append(tool + " 100 - (FPR)")
        header.append(tool + " (P)")

    table = []
    raw_table = []
    for error in crunched_data[0].keys():
        row = []
        row.append(error)
        for i in range(0, len(tool_list)):
            dr = (float(crunched_data[i][error]["TP"]) / float(crunched_data[i][error]["count"])) * 100
            fpr = 100 - (float(crunched_data[i][error]["FP"]) / crunched_data[i][error]["count"] * 100)
            prod = math.sqrt(dr * fpr)
            row = row + [dr, fpr, prod]
        table.append(row)

    for error in crunched_data[0].keys():
        row = [error]
        total_tp = 0
        total_fp = 0
        for i in range(0, len(tool_list)):
            raw_tp = crunched_data[i][error]["TP"]
            raw_fp = crunched_data[i][error]["FP"]
            total_tp += raw_tp
            total_fp += raw_fp
            row = row + [raw_tp, raw_fp, crunched_data[i][error]["count"]]
        raw_table.append(row)

    count_dict = info.get_count_dict()
    test_total = info.get_total()
    average = ["Average"]
    for column in range(1, len(table[0])):
        if column % 3 == 0:
            prod = math.sqrt(average[-1] * average[-2])
            average.append(prod)
            continue
        sum = 0
        for row in range(0, len(table)):
            error = table[row][0]
            sum += float(table[row][column]) * (float(count_dict[error]) / test_total)

        else:
            average.append(sum)


    table.append(average)
    print tabulate(table, headers=header, tablefmt="fancy_grid")
    print tabulate(table, headers=header, tablefmt="simple")

    print tabulate(raw_table, headers=["Error", "True Positive Count", "False Positive Count", "Tests Run"])
def run_itc_benchmark(log_location):
    global tools
    tools = [FramaC(path, log_location)]
    output_dicts = map(lambda x: x.run(), tools)
    names_list = map(lambda x: x.get_name(), tools)
    data_list = map(lambda x: crunch_data(x), output_dicts)
    tabulate_itc_criteria(names_list, data_list)
    map(lambda x : x.cleanup(), tools)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print "Needed: Path to Benchmark as arguments"
    else:
        path = sys.argv[1]
        if sys.argv[2] == "rv":
            run_rv_benchmark()
        if sys.argv[2] == "itc":
            run_itc_benchmark(sys.argv[3])
