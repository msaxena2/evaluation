from tool import Tool
from utils import Info
import os
import subprocess

class Valgrind(Tool):

    def run(self, verbose=False, log_location=None):
        output_dict = {}
        spec_dict = self.info.get_spec_dict()
        for i in xrange(1, len(spec_dict.keys()) + 1):
            output_dict[i] = {"count": spec_dict[i]["count"], "TP": 0, "FN": 0}
            for j in range(i, spec_dict[i]["count"]):
                arg = str('%03d' % i) + str('%03d' % j)
                output = subprocess.check_call(["valgrind", "./01.w_Defects/01_w_Defects", arg])
                if output != 0:
                    output_dict[i]["TP"] += 1
                output = subprocess.check_call(["valgrind", "./02.wo_Defects/02_wo_Defects", arg])
                if output == 0:
                    output_dict[i]["FN"] += 1
        print spec_dict

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

    def analyze(self):
        Tool.analyze(self)

    def cleanup(self):
        Tool.cleanup(self)
