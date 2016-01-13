__author__ = 'manasvi'
from tool import Tool
import os
import subprocess32 as subprocess
import signal
from tabulate import tabulate

class TimeoutException(Exception):
    pass

class CompcertRV(Tool):

    def signal_handler(self, signum, frame):
        raise TimeoutException("Timed out!")

    def run(self, verbose=False, log_location=None):
        output_dict = {"TP": 0, "FP": 0}
        error_code_dict = {}
        total = 0
        os.chdir(self.benchmark_path)
        for dir in filter(lambda x : os.path.isdir(x), os.listdir(os.getcwd())):
            os.chdir(dir)
            print "In Directory: " + os.getcwd()
            file_list = os.listdir(os.getcwd())
            for c_file in filter(lambda y : y.endswith(".c"), file_list):
                unsupported_set = set()
                if "link" in c_file:
                    unsupported_set.add('-'.join(c_file.split('-')[:1]))
                    continue
                if "-good" in c_file:
                    error_code = c_file.split("-good")[0]
                    is_bad = False
                else:
                    error_code = c_file.split("-bad")[0]
                    is_bad = True
                if error_code not in error_code_dict:
                    error_code_dict[error_code] = {"TP": " ", "FP": " "}
                signal.signal(signal.SIGALRM, self.signal_handler)
                signal.alarm(100)
                try:
                    command = ["ccomp", "-fstruct-passing", "-interp", "-trace", c_file]
                    print command
                    subprocess.check_call(command)
                except subprocess.CalledProcessError:
                    if is_bad:
                        output_dict["TP"] += 1
                        error_code_dict[error_code]["TP"] = "CompCert"
                    else:
                        output_dict["FP"] += 1
                        error_code_dict[error_code]["FP"] = "CompCert"
                except TimeoutException:
                    pass
                finally:
                    signal.alarm(0)
            os.chdir(self.benchmark_path)
        return output_dict, error_code_dict


    def tabulate(self, error_code_dict):
        table = []
        for key in error_code_dict.keys():
            table.append([key, error_code_dict[key]["TP"], error_code_dict[key]["FP"]])
        print tabulate(table, headers=["Error-Code", "TP", "FP"], tablefmt="fancy_grid")


    def __init__(self, benchmark_path):
        self.benchmark_path = os.path.expanduser(benchmark_path)

    def analyze(self):
        output_dict, error_dict = self.run()
        # Hacky; Needs Change
        total = 312
        print "Total Tests Run: " + str(total)
        print "% true positives (valgrind): " + str(float(output_dict["TP"])/(total/2) * 100)
        print "% false positives (valgrind): " + str(float(output_dict["FP"])/(total/2) * 100)
        self.tabulate(error_dict)


    def cleanup(self):
        Tool.cleanup(self)