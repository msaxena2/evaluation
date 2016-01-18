import os
import subprocess

from Tools.rv_benchmark.tool import Tool
from utils.utils import Info
import progressbar

class Valgrind(Tool):

    def run(self, verbose=False, log_location=None):
        output_dict = {}
        print "here"
        spec_dict = self.info.get_spec_dict()
        os.chdir(self.benchmark_path)
        for i in range(1, len(spec_dict.keys()) + 1):
            output_dict[i] = {"count": spec_dict[i]["count"], "TP": 0, "FN": 0}
            print self.name + " being tested on file " + str(i)
            for j in range(i, spec_dict[i]["count"]):
                arg = [str('%03d' % i) + str('%03d' % j)]
                try:
                    output_w = subprocess.check_output(["valgrind", "--error-exitcode=-1","./01.w_Defects/01_w_Defects"] + arg)
                except subprocess.CalledProcessError:
                    output_dict[i]["TP"] += 1
                try:
                    output_wo = subprocess.check_output(["valgrind", "--error-exitcode=-1","./02.wo_Defects/02_wo_Defects"] + arg)
                    # Update Data record
                except subprocess.CalledProcessError:
                    output_dict[i]["FN"] += 1
                if verbose:
                    whole_path = os.path.expanduser(log_location)
                    mode = 'a'
                    if not os.path.exists(whole_path) or (i == 1 and j == 0):
                        mode = 'w+'
                    with open(whole_path, mode) as output_file:
                            output_file.write(output_w)
                            output_file.write(output_wo)
        print output_dict



    def init(self):
        os.chdir(os.path.expanduser(self.benchmark_path))
        subprocess.check_call(["./bootstrap"])
        subprocess.check_call(["automake"])
        subprocess.check_call(["autoconf"])
        subprocess.check_call(["./configure"])
        subprocess.check_call(["make"])

    def __init__(self, benchmark_path, info_csv):
        self.info = Info(info_csv)
        self.benchmark_path = benchmark_path
        self.name = "Valgrind + GCC"

    def analyze(self):
        Tool.analyze(self)

    def cleanup(self):
        Tool.cleanup(self)
