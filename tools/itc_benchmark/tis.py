import os
import subprocess
import utils.external_info
from tools.rv_benchmark.tool import Tool
from utils.external_info import Info
import progressbar
import signal
import re
from glob import glob
from utils.logger import Logger

class TimeoutException(Exception):
    pass


class TIS(Tool):
    def signal_handler(self, signum, frame):
        raise TimeoutException("Timed out!")

    def analyze_output(self, output, file_name):
        return "ERROR" in output.upper()




    def get_tis_command(self, cur_dir, file_prefix, temp_dir_name, vflag, header_file_path):
        cur_path = os.path.join(self.benchmark_path, cur_dir)
        temp_path = os.path.join(cur_path, temp_dir_name)
        if not os.path.exists(temp_path):
            os.mkdir(temp_path)

        relevant_file_path = os.path.join(cur_path, file_prefix + ".c")
        bootstrap_file_path = os.path.join(temp_path, file_prefix + "-temp.c")
        utils.external_info.bootstrap_file(relevant_file_path, bootstrap_file_path, vflag, "SH")
        return ["tis", bootstrap_file_path]

    def run(self):
        relevant_dirs = ["01.w_Defects", "02.wo_Defects"]
        output_dict = {}

        for cur_dir in relevant_dirs:
            spec_dict = self.info.get_spec_dict()
            mapping_dict = self.info.get_file_mapping()
            for i in range(1, len(spec_dict.keys()) + 1):
                if i not in output_dict:
                    output_dict[i] = {"count": spec_dict[i]["actual_count"], "TP": 0, "FP": 0}
                if (i, -1) in self.info.get_ignore_list():
                    continue
                file_prefix = mapping_dict[i]
                print self.name + " being tested on folder " + cur_dir + " and file " + file_prefix
                # bar = progressbar.ProgressBar(redirect_stdout=True)
                verdict = False
                output = ""
                for j in range(1, spec_dict[i]["count"]):
                    if (i, j) in self.info.get_ignore_list():
                        continue
                    vflag = str('%03d' % j)
                    try:
                        original_header_path = os.path.join(self.benchmark_path, "include")
                        new_header_path =  os.path.join(original_header_path, "tis_temp")
                        tis_command = self.get_tis_command(cur_dir, file_prefix, "tis_dir", vflag, new_header_path)
                        print " ".join(tis_command)
                        if len(tis_command) != 0:
                            signal.signal(signal.SIGALRM, self.signal_handler)
                            #signal.alarm(10)
                            output = subprocess.check_output(tis_command, stderr=subprocess.STDOUT)
                            print output
                            verdict = self.analyze_output(output, file_prefix)
                            if verdict:
                                if "w_Defects" in cur_dir:
                                    output_dict[i]["TP"] += 1
                                    self.logger.log_output(output, file_prefix + ".c", cur_dir, str(j), "TP")
                                else:
                                    output_dict[i]["FP"] += 1
                                    self.logger.log_output(output, file_prefix + ".c", cur_dir, str(j), "FP")

                    except subprocess.CalledProcessError as e:
                        signal.alarm(0)
                        self.logger.log_output(output, file_prefix + ".c", cur_dir, str(j), "NEG")
                        #error with the plugin
                        continue

                    except TimeoutException:
                        self.logger.log_output(output, file_prefix + ".c", cur_dir, str(j), "TO")
                        continue
                    finally:
                        if not verdict:
                            self.logger.log_output(output, file_prefix + ".c", cur_dir, str(j), "NEG")
                        signal.alarm(0)
        return output_dict

    def get_name(self):
        return self.name

    def __init__(self, benchmark_path, log_path):
        self.info = Info()
        self.benchmark_path = benchmark_path
        self.name = "TIS"
        self.logger = Logger(log_path, self.name)

    def analyze(self):
        Tool.analyze(self)

    def cleanup(self):
        Tool.cleanup(self)
        self.logger.close_log()
