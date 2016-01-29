import os
import subprocess32 as subprocess

from tools.rv_benchmark.tool import Tool
from utils.external_info import Info
import signal
from utils.logger import Logger
import re
import utils

class TimeoutException(Exception):
    pass

class Valgrind(Tool):

    def signal_handler(self, signum, frame):
        raise TimeoutException("Timed out!")



    def run(self, verbose=False, log_location=None):
        output_dict = {}
        spec_dict = self.info.get_spec_dict()
        ignore_list = self.info.get_ignore_list()
        os.chdir(self.benchmark_path)
        mapping_dict = self.info.get_file_mapping()
        relevant_dirs = ["01.w_Defects", "02.wo_Defects"]
        for cur_dir in relevant_dirs:
            for i in range(1, len(spec_dict.keys()) + 1):
                if i not in output_dict:
                    output_dict[i] = {"count": spec_dict[i]["actual_count"], "TP": 0, "FP": 0}
                if (i, -1) in ignore_list:
                    continue
                file_prefix = mapping_dict[i]
                print self.name + " being tested on file " + str(i)
                executable_name = cur_dir.split('.')[0] + "_" + cur_dir.split('.')[-1]
                #bar = progressbar.ProgressBar()
                for j in range(1, spec_dict[i]["count"]):
                    if (i, j) in ignore_list:
                        continue
                    arg = str('%03d' % i) + str('%03d' % j)
                    valgrind_command = ["valgrind", "--error-exitcode=30", os.path.join(self.benchmark_path, cur_dir, executable_name), arg]
                    print " ".join(valgrind_command)
                    result = "NEG"
                    output = ""
                    try:
                        #output = subprocess.check_output(kcc_command, stderr=subprocess.STDOUT, timeout=4)
                        process = subprocess.Popen(valgrind_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        exit_code = process.wait(timeout=16)
                        output = process.stdout.read() + process.stderr.read()
                        if exit_code != 0:
                            result="POS"


                    except subprocess.TimeoutExpired as e:
                        result = "TO"

                    finally:
                        process.kill()
                        if result == "POS":
                            if "w_Defects" in cur_dir:
                                output_dict[i]["TP"] += 1
                                self.logger.log_output(output, file_prefix + ".c", cur_dir, j, "TP")
                            else:
                                output_dict[i]["FP"] += 1
                                self.logger.log_output(output, file_prefix + ".c", cur_dir, j, "FP")
                        elif result == "TO":
                            self.logger.log_output(output, file_prefix + ".c", cur_dir, j, "TO")
                        else:
                            self.logger.log_output(output, file_prefix + ".c", cur_dir, j, "NEG")



        return output_dict

    def get_name(self):
        return self.name


    def __init__(self, benchmark_path, log_file_path):
        os.chdir(os.path.expanduser(benchmark_path))

        # subprocess.check_call(["./bootstrap"])
        # subprocess.check_call(["./configure", "CC=clang", "LD=clang", "CFLAGS=-flint"])
        # compile_output = subprocess.check_call(["make", "-j4"], stderr=subprocess.STDOUT)


        self.info = Info()
        self.benchmark_path = benchmark_path
        self.name = "Valgrind+GCC"
        self.logger = Logger(log_file_path, self.name)

    def analyze(self):
        Tool.analyze(self)

    def cleanup(self):
        Tool.cleanup(self)
        self.logger.close_log()
