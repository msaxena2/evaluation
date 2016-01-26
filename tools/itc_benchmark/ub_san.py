import os
import subprocess

from tools.rv_benchmark.tool import Tool
from utils.external_info import Info
import signal

class TimeoutException(Exception):
    pass

class UBSan(Tool):

    def signal_handler(self, signum, frame):
        raise TimeoutException("Timed out!")

    def run(self, verbose=False, log_location=None):
        output_dict = {}
        spec_dict = self.info.get_spec_dict()
        os.chdir(self.benchmark_path)
        for i in range(1, len(spec_dict.keys()) + 1):
            if i not in output_dict:
                output_dict[i] = {"count": spec_dict[i]["count"], "TP": 0, "FP": 0}
            print self.name + " being tested on file " + str(i)
            #bar = progressbar.ProgressBar()
            for j in range(1, spec_dict[i]["count"]):
                arg = [str('%03d' % i) + str('%03d' % j)]
                try:
                    signal.signal(signal.SIGALRM, self.signal_handler)
                    signal.alarm(10)
                    output_w = subprocess.check_output(["./01.w_Defects/01_w_Defects"] + arg)#, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError:
                    output_dict[i]["TP"] += 1
                except TimeoutException:
                    pass
                try:
                    signal.alarm(10)
                    output_wo = subprocess.check_output(["./02.wo_Defects/02_wo_Defects"] + arg)#, stderr=subprocess.STDOUT)
                except subprocess.CalledProcessError:
                    output_dict[i]["FP"] += 1
                except TimeoutException:
                    continue
                finally:
                    #reset the alarm
                    signal.alarm(0)
                if verbose:
                    whole_path = os.path.expanduser(log_location)
                    mode = 'a'
                    if not os.path.exists(whole_path) or (i == 1 and j == 0):
                        mode = 'w+'
                    with open(whole_path, mode) as output_file:
                        output_file.write(output_w)
                        output_file.write(output_wo)
        return output_dict

    def get_name(self):
        return self.name


    def __init__(self, benchmark_path):
        os.chdir(os.path.expanduser(benchmark_path))
        subprocess.check_call(["./bootstrap"])
        subprocess.check_call(["automake"])
        subprocess.check_call(["autoconf"])
        subprocess.check_call(["./configure", "CC=clang", "CFLAGS=-fsanitize=undefined -fsanitize=thread -fsanitize=address"])
        subprocess.check_call(["make"])
        self.info = Info()
        self.benchmark_path = benchmark_path
        self.name = "Clang"

    def analyze(self):
        Tool.analyze(self)

    def cleanup(self):
        Tool.cleanup(self)
