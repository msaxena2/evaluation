from tool import Tool
from utils import Info
import os
import subprocess

class Valgrind(Tool):

    def run(self, verbose=False, log_location=None):
        for i in xrange(1, len(self.info.get_spec_dict().keys())):
            print i


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
