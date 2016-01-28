import os
import subprocess

from tools.rv_benchmark.tool import Tool
from utils.external_info import Info
import signal
from utils.logger import Logger
import re
import utils

class TimeoutException(Exception):
    pass

class UBSan(Tool):

    def signal_handler(self, signum, frame):
        raise TimeoutException("Timed out!")

    def get_clang_command(self, cur_dir, file_prefix, temp_dir_name, vflag):
        cur_path = os.path.join(self.benchmark_path, cur_dir)
        temp_path = os.path.join(cur_path, temp_dir_name)
        if not os.path.exists(temp_path):
            os.mkdir(temp_path)

        relevant_file_path = os.path.join(cur_path, file_prefix + ".c")
        bootstrap_file_path = os.path.join(temp_path, file_prefix + "-temp.c")
        utils.external_info.bootstrap_file(relevant_file_path, bootstrap_file_path, vflag)
        return ["clang", "-fsanitize=undefined", "-Werror", "-Wpedantic", "-Wall", "-Wextra", "-Wno-unused", "-lm", "-o", os.path.join(temp_path, file_prefix + "-temp.out"), bootstrap_file_path, os.path.join(self.benchmark_path, "extern.c")]


    def get_run_command(self, cur_dir, file_prefix, temp_dir_name):
        relevant_file_path = os.path.join(self.benchmark_path, temp_dir_name, file_prefix + "-temp.out")
        if os.path.exists(relevant_file_path):
            return [relevant_file_path]
        return []



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
                #bar = progressbar.ProgressBar()
                for j in range(1, spec_dict[i]["count"]):
                    if (i, j) in ignore_list:
                        continue
                    vflag = str('%03d' % j)
                    gcc_command = self.get_clang_command(cur_dir, file_prefix, "ubsan_temp", vflag)
                    result = "NEG"
                    print " ".join(gcc_command)
                    try:
                        signal.signal(signal.SIGALRM, self.signal_handler)
                        signal.alarm(120)
                        output = subprocess.check_output(gcc_command, stderr=subprocess.STDOUT)
                        valgrind = self.get_run_command(cur_dir, file_prefix, "ubsan_temp")
                        output = subprocess.check_output(valgrind, stderr=subprocess.STDOUT)

                    except subprocess.CalledProcessError as e:
                        result = "POS"

                    except TimeoutException:
                        result = "TO"

                    finally:
                        signal.alarm(0)
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
        self.info = Info()
        self.benchmark_path = benchmark_path
        self.name = "UBSan"
        self.logger = Logger(log_file_path, self.name)

    def analyze(self):
        Tool.analyze(self)

    def cleanup(self):
        Tool.cleanup(self)
        self.logger.close_log()
