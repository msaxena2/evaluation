__author__ = 'manasvi'
from tool import Tool
import os
import subprocess32 as subprocess
import signal
from tabulate import tabulate

class TimeoutException(Exception):
    pass

class UBSanRV(Tool):

    def signal_handler(self, signum, frame):
        raise TimeoutException("Timed out!")

    def run(self, verbose=False, log_location=None):
        output_dict = {"compile": {"TP": 0, "FP": 0}, "runtime": {"TP": 0, "FP": 0}}
        error_code_dict = {}
        total = 0
        os.chdir(self.benchmark_path)
        for dir in filter(lambda x : os.path.isdir(x), os.listdir(os.getcwd())):
            os.chdir(dir)
            print "In Directory: " + os.getcwd()
            file_list = os.listdir(os.getcwd())
            for c_file in filter(lambda y : y.endswith(".c"), file_list):
                c_files = []
                exec_name = c_file.split('.')[0]
                if "link" in c_file:
                    if "link1" not in c_file:
                        continue
                    exec_name = exec_name.replace("-link1", "",)
                    c_files.append(c_file)
                    i = 2
                    while True:
                        split = c_file.split("-link1")
                        link_file_name = split[0] + "-link" + str(i) + split[1]
                        if link_file_name in file_list:
                            c_files.append(link_file_name)
                            i += 1
                            continue
                        break
                else:
                    c_files = [c_file]


                out_name = exec_name + ".out"
                total += 1
                if "-good" in c_file:
                    error_code = c_file.split("-good")[0]
                    is_bad = False
                else:
                    error_code = c_file.split("-bad")[0]
                    is_bad = True
                if error_code not in error_code_dict:
                    error_code_dict[error_code] = {"TP": " ", "FP": " "}
                signal.signal(signal.SIGALRM, self.signal_handler)
                signal.alarm(5)
                try:
                    mode = "compile"
                    command = ["clang", "-Wpedantic", "-Wall", "-Wextra", "-g", "-fsanitize=undefined", "-std=c11"] + c_files + ["-o", out_name]
                    #print command
                    subprocess.check_output(command, stderr=subprocess.STDOUT)
                    mode = "runtime"
                    val_command = ["./" + out_name]
                    #print val_command
                    subprocess.check_output(val_command, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError as error:
                    if is_bad:
                        output_dict[mode]["TP"] += 1
                        error_code_dict[error_code]["TP"] = mode
                    else:
                        output_dict[mode]["FP"] += 1
                        error_code_dict[error_code]["FP"] = mode
                except TimeoutException:
                    pass
                finally:
                    signal.alarm(0)
            os.chdir(self.benchmark_path)
        return output_dict, error_code_dict, total

    def runtime_clang(self, output_dict, total):
        print "% true positives (runtime): " + str(float(output_dict["runtime"]["FP"])/(total/2) * 100)
        print "% false positives (runtime): " + str(float(output_dict["runtime"]["FP"])/(total/2) * 100)

    def compile_clang(self, output_dict, total):
        print "% True Positives (compile): " + str(float(output_dict["compile"]["TP"])/(total/2) * 100)
        print "% False Poistives (compile): " + str(float(output_dict["compile"]["FP"])/(total/2) * 100)
    def init(self):
        pass

    def tabulate(self, error_code_dict):
        table = []
        for key in error_code_dict.keys():
            table.append([key, error_code_dict[key]["TP"], error_code_dict[key]["FP"]])
        print tabulate(table, headers=["Error-Code", "TP", "FP"], tablefmt="fancy_grid")


    def __init__(self, benchmark_path):
        self.benchmark_path = os.path.expanduser(benchmark_path)

    def analyze(self):
        output_dict, error_dict, total = self.run()
        print "Total Tests Run: " + str(total)
        self.runtime_clang(output_dict, total)
        self.compile_clang(output_dict, total)
        self.tabulate(error_dict)


    def cleanup(self):
        Tool.cleanup(self)
