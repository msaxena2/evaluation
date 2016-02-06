import os
import subprocess32 as subprocess

from tools.rv_benchmark.tool import Tool
from utils.external_info import Info
import signal
from utils.logger import Logger
import re
import utils
import pickle
from utils.make_pipeline import MakePipeline


class TimeoutException(Exception):
    pass

class Valgrind(Tool):

    def signal_handler(self, signum, frame):
        raise TimeoutException("Timed out!")


    def pickle_set(self, tp_set, fp_set):
        with open(self.tp_pickle_file, 'w+') as tp:
            pickle.dump(tp_set, tp)
        with open(self.fp_pickle_file, 'w+') as fp:
            pickle.dump(fp_set, fp)


    def run(self, verbose=False, log_location=None):
        self.build()
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
                for j in range(1, spec_dict[i]["count"] + 1):
                    if (i, j) in ignore_list:
                        continue
                    arg = str('%03d' % i) + str('%03d' % j)
                    kcc_command = ["valgrind", "--error-exitcode=10", os.path.join(self.benchmark_path, cur_dir, executable_name), arg]
                    print kcc_command
                    result = "NEG"
                    output = ""
                    try:
                        #output = subprocess.check_output(kcc_command, stderr=subprocess.STDOUT, timeout=4)
                        process = subprocess.Popen(kcc_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        exit = process.wait(timeout=3)
                        output = process.stderr.read()
                        print output
                        if exit != 0:
                            result = "POS"


                    except subprocess.TimeoutExpired as e:
                        result = "TO"

                    finally:
                        process.kill()
                        signal.alarm(0)
                        if result == "POS":
                            if "w_Defects" in cur_dir:
                                output_dict[i]["TP"] += 1
                                self.logger.log_output(output, file_prefix + ".c", cur_dir, j, "TP")
                                self.tp_pickle_list.append((i, j))
                            else:
                                output_dict[i]["FP"] += 1
                                self.logger.log_output(output, file_prefix + ".c", cur_dir, j, "FP")
                                self.fp_pickle_list.append((i, j))
                        elif result == "TO":
                            self.logger.log_output(output, file_prefix + ".c", cur_dir, j, "TO")
                        else:
                            self.logger.log_output(output, file_prefix + ".c", cur_dir, j, "NEG")

        print self.tp_pickle_list
        self.pickle_set(set(self.tp_pickle_list), set(self.fp_pickle_list))
        return output_dict

    def get_name(self):
        return self.name



    def build(self):
        if "Makefile" in os.listdir(os.getcwd()):
            subprocess.check_call(["make", "clean"])
        subprocess.check_call(["autoreconf", "--install"])
        subprocess.check_call(["automake"])
        subprocess.check_call(["./configure", "CFLAGS=-g"])
        subprocess.check_call(["make"], stderr=subprocess.STDOUT)


    def __init__(self, benchmark_path, log_file_path):
        self.pipeline = MakePipeline(benchmark_path)
        self.name = "Valgrind"
        self. logger = Logger(log_file_path, self.name)
        self.output_dict = {}
        os.chdir(os.path.expanduser(benchmark_path))

    def analyze_output(self, stdout, stderr, cur_dir, i, j):
        Tool.analyze(self)
        if i not in self.output_dict:
            self.output_dict[i] = {"count": 0, "TP":0, "FP":0}
        self.output_dict[i]["count"] += 1





    def cleanup(self):
        Tool.cleanup(self)
        self.logger.close_log()
