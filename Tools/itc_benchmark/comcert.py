import os
import subprocess
import utils.external_info
from tools.rv_benchmark.tool import Tool
from utils.external_info import Info
import progressbar
import signal


class TimeoutException(Exception):
    pass


class Compcert(Tool):
    def signal_handler(self, signum, frame):
        raise TimeoutException("Timed out!")

    def get_compcert_command(self, cur_dir, file_prefix):
        cil_file = os.path.join(self.benchmark_path, cur_dir, "compcert_temp", file_prefix + "-temp.cil.c")
        if not os.path.exists(cil_file):
            return []

        utils.external_info.sanitize_cil_file(cil_file)
        return ["ccomp", "-interp", "-fbitfields", "-fstruct-passing", cil_file]

    def run(self, verbose=False, log_location=None):
        relevant_dirs = ["02.wo_Defects", "01.w_Defects"]
        output_dict = {}
        for cur_dir in relevant_dirs:
            spec_dict = self.info.get_spec_dict()
            mapping_dict = self.info.get_file_mapping()
            for i in range(1, len(spec_dict.keys()) + 1):
                if i not in output_dict:
                    output_dict[i] = {"count": spec_dict[i]["count"], "TP": 0, "FP": 0}
                file_prefix = mapping_dict[i]
                print self.name + " being tested on folder " + cur_dir + " and file " + file_prefix + ".c"
                # bar = progressbar.ProgressBar(redirect_stdout=True)
                for j in range(1, spec_dict[i]["count"]):
                    vflag = str('%03d' % j)
                    cilly_command = utils.external_info.get_cilly_commmand(self.benchmark_path, cur_dir, file_prefix,
                                                                           "compcert_temp", vflag)
                    if len(cilly_command) == 0:
                        break
                    try:
                        subprocess.check_output(cilly_command, stderr=subprocess.STDOUT)
                    except subprocess.CalledProcessError:
                        continue
                    try:
                        compcert_command = self.get_compcert_command(cur_dir, file_prefix)
                        if len(compcert_command) != 0:
                            signal.signal(signal.SIGALRM, self.signal_handler)
                            signal.alarm(10)
                            subprocess.check_output(compcert_command)  # , stderr=subprocess.STDOUT)
                    except subprocess.CalledProcessError as e:
                        if "Fatal error; compilation aborted." in e.output:
                            continue
                        if "w_Defects" in cur_dir:
                            output_dict[i]["TP"] += 1
                        else:
                            output_dict[i]["FP"] += 1
                    except TimeoutException:
                        continue
                    finally:
                        signal.alarm(0)
        return output_dict

    def get_name(self):
        return self.name

    def __init__(self, benchmark_path):
        self.info = Info()
        self.benchmark_path = benchmark_path
        self.name = "Compcert"

    def analyze(self):
        Tool.analyze(self)

    def cleanup(self):
        Tool.cleanup(self)
