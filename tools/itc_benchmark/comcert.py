import os
import subprocess
import utils.external_info
from tools.rv_benchmark.tool import Tool
from utils.external_info import Info
import progressbar
import signal
import utils.logger


class TimeoutException(Exception):
    pass


class Compcert(Tool):
    def signal_handler(self, signum, frame):
        raise TimeoutException("Timed out!")

    def get_compcert_command(self, cur_dir, file_prefix, temp_dir_name, vflag):
        cur_path = os.path.join(self.benchmark_path, cur_dir)
        temp_path = os.path.join(cur_path, temp_dir_name)
        if not os.path.exists(temp_path):
            os.mkdir(temp_path)

        relevant_file_path = os.path.join(cur_path, file_prefix + ".c")
        bootstrap_file_path = os.path.join(temp_path, file_prefix + "-temp.c")
        utils.external_info.bootstrap_file(relevant_file_path, bootstrap_file_path, vflag)
        return ["ccomp", "-interp", "-fbitfields", "-fstruct-passing",
                "-I" + os.path.join(self.benchmark_path, "include"),
                bootstrap_file_path]

    def run(self):
        relevant_dirs = ["01.w_Defects", "02.wo_Defects"]
        output_dict = {}
        ignore_list = self.info.get_ignore_list()
        for cur_dir in relevant_dirs:
            spec_dict = self.info.get_spec_dict()
            mapping_dict = self.info.get_file_mapping()
            for i in range(1, len(spec_dict.keys()) + 1):
                if i not in output_dict:
                    output_dict[i] = {"count": spec_dict[i]["actual_count"], "TP": 0, "FP": 0}
                if (i, -1) in ignore_list:
                    continue
                file_prefix = mapping_dict[i]
                print self.name + " being tested on folder " + cur_dir + " and file " + file_prefix + ".c"
                # bar = progressbar.ProgressBar(redirect_stdout=True)
                for j in range(1, spec_dict[i]["count"]):
                    if (i, j) in ignore_list:
                        continue
                    vflag = str('%03d' % j)
                    try:
                        written = False
                        compcert_command = self.get_compcert_command(cur_dir, file_prefix, "bootstrap_dir", vflag)
                        print compcert_command
                        if len(compcert_command) != 0:
                            signal.signal(signal.SIGALRM, self.signal_handler)
                            signal.alarm(10)
                            subprocess.check_output(compcert_command, stderr=subprocess.STDOUT)
                    except subprocess.CalledProcessError as e:
                        written = True
                        print e.output
                        if "ERROR" not in e.output.upper() and "UNDEFINED" not in e.output.upper():
                            self.logger.log_output(e.output, file_prefix + ".c", cur_dir, j, "NEG")
                            continue
                        if "Stuck state: calling" in e.output:
                            self.logger.log_output(e.output, file_prefix + ".c", cur_dir, j, "NEG")
                            continue
                        if "w_Defects" in cur_dir:
                            output_dict[i]["TP"] += 1
                            self.logger.log_output(e.output, file_prefix + ".c", cur_dir, j, "TP")
                        else:
                            output_dict[i]["FP"] += 1
                            self.logger.log_output(e.output, file_prefix + ".c", cur_dir, j, "FP")


                    except TimeoutException:
                        written = True
                        self.logger.log_output(e.output, file_prefix + ".c", cur_dir, j, "TO")
                        continue
                    finally:
                        if not written:
                            self.logger.log_output(e.output, file_prefix + ".c", cur_dir, j, "NEG")
                        signal.alarm(0)
        return output_dict

    def get_name(self):
        return self.name

    def __init__(self, benchmark_path, log_file_path):
        self.info = Info()
        self.benchmark_path = benchmark_path
        self.name = "Compcert"
        self.logger = utils.logger.Logger(log_file_path, self.name)

    def analyze(self):
        Tool.analyze(self)

    def cleanup(self):
        Tool.cleanup(self)
        self.logger.close_log()
