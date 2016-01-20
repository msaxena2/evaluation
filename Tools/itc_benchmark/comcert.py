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

    def get_cilly_commmand(self, cur_dir, file_prefix, vflag):
        cur_path = os.path.join(self.benchmark_path, cur_dir)
        temp_path = os.path.join(cur_path, "compcert_temp")
        if not os.path.exists(temp_path):
            os.mkdir(temp_path)

        relevant_file_path = os.path.join(cur_path, file_prefix + ".c")
        if not os.path.exists(relevant_file_path):
            return []
        bootstrap_file_path = os.path.join(temp_path, file_prefix + "-temp.c")
        utils.external_info.bootstrap_file(relevant_file_path, bootstrap_file_path, vflag)
        cilly_command = ["cilly", "--merge", "--keepmerged", "--save-temps=" + temp_path,
                         "-I" + os.path.join(self.benchmark_path, "include"),
                         bootstrap_file_path]
        return cilly_command


    def get_compcert_command(self, cur_dir, file_prefix):
        cil_file = os.path.join(self.benchmark_path, cur_dir, "compcert_temp", file_prefix + "-temp.cil.c")
        if not os.path.exists(cil_file):
            return []

        utils.external_info.sanitize_cil_file(cil_file)
        return ["ccomp", "-interp", "-fbitfields", cil_file]

    def run(self, verbose=False, log_location=None):
        relevant_dirs = ["01.w_Defects", "02.wo_Defects"]
        for cur_dir in relevant_dirs:
            output_dict = {}
            spec_dict = self.info.get_spec_dict()
            mapping_dict = self.info.get_file_mapping()
            for i in range(1, len(spec_dict.keys()) + 1):
                output_dict[i] = {"count": spec_dict[i]["count"], "TP": 0, "FP": 0}
                file_prefix = mapping_dict[i]
                print self.name + " being tested on folder " + cur_dir + " and file " + file_prefix + ".c"
                #bar = progressbar.ProgressBar(redirect_stdout=True)
                for j in range(1, spec_dict[i]["count"]):
                    vflag = str('%03d' % j)
                    cilly_command = self.get_cilly_commmand(cur_dir, file_prefix, vflag)
                    if len(cilly_command) == 0:
                        break
                    try:
                        subprocess.check_output(cilly_command)#, stderr=subprocess.STDOUT)
                    except subprocess.CalledProcessError:
                        continue
                    try:
                        compcert_command = self.get_compcert_command(cur_dir, file_prefix)
                        if len(compcert_command) != 0:
                            signal.signal(signal.SIGALRM, self.signal_handler)
                            signal.alarm(10)
                            subprocess.check_output(compcert_command)#, stderr=subprocess.STDOUT)
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
