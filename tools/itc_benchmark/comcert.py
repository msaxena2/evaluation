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


    def get_compcert_command(self, cur_dir, file_prefix, temp_dir_name, vflag):
        cur_path = os.path.join(self.benchmark_path, cur_dir)
        temp_path = os.path.join(cur_path, temp_dir_name)
        if not os.path.exists(temp_path):
            os.mkdir(temp_path)

        relevant_file_path = os.path.join(cur_path, file_prefix + ".c")
        if not os.path.exists(relevant_file_path):
            return []
        bootstrap_file_path = os.path.join(temp_path, file_prefix + "-temp.c")
        utils.external_info.bootstrap_file(relevant_file_path, bootstrap_file_path, vflag)
        return ["ccomp", "-interp", "-fbitfields", "-fstruct-passing",
                "-I" + os.path.join(self.benchmark_path, "include"),
                bootstrap_file_path]



    def run(self, verbose=False, log_location=None):
        relevant_dirs = ["02.w_Defects", "02.wo_Defects"]
        output_dict = {}
        log_file = None
        if log_location is not None:
            log_file = open(log_location, 'w+')

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
                    try:
                        compcert_command = self.get_compcert_command(cur_dir, file_prefix, "compcert_temp", vflag)
                        print compcert_command
                        if len(compcert_command) != 0:
                            signal.signal(signal.SIGALRM, self.signal_handler)
                            signal.alarm(10)
                            subprocess.check_output(compcert_command, stderr=subprocess.STDOUT)
                    except subprocess.CalledProcessError as e:
                        print e.output
                        if "ERROR" not in e.output or "Error" not in e.output:
                            result = False
                        elif "Stuck State: call" in e.output:
                            result = False
                        else:
                            result = True
                        if "w_Defects" in cur_dir and result:
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
