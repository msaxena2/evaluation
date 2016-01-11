__author__ = 'manasvi'
from tool import Tool
import os
import subprocess

class ValgrindRV(Tool):

    def run(self, verbose=False, log_location=None):
        output_dict = {"TP": 0, "FP": 0}
        error_code_dict = {}
        os.chdir(self.benchmark_path)
        for dir in filter(lambda x : os.path.isdir(x), os.listdir(os.getcwd())):
            os.chdir(dir)
            print "In Directory: " + os.getcwd()
            for c_file in filter(lambda y : y.endswith(".c"), os.listdir(os.getcwd())):
                    exec_name = c_file.split('.')[0]
                    out_name = exec_name + ".out"
                    subprocess.check_call(["gcc", c_file, "-o", out_name])
                    if "-good" in c_file:
                        error_code = c_file.split("-good")[0]
                        is_bad = False
                    else:
                        error_code = c_file.split("-bad")[0]
                        is_bad = True
                    error_code_dict[error_code] = {"TP": 0, "FN": 0}
                    try:
                        subprocess.check_output(["valgrind", "--error-exitcode=-1", "./out_name"], stderr=subprocess.STDOUT, shell=True)
                    except subprocess.CalledProcessError:
                        if is_bad:
                            output_dict["TP"] += 1
                            error_code_dict[error_code]["TP"] = 1
                        else:
                            output_dict["FP"] += 1
                            error_code_dict[error_code]["FN"] = 1
            os.chdir(self.benchmark_path)
            print 



    def init(self):
        pass

    def __init__(self, benchmark_path):
        self.benchmark_path = benchmark_path

    def analyze(self):
        Tool.analyze(self)

    def cleanup(self):
        Tool.cleanup(self)
