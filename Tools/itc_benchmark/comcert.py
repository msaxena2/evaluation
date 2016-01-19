import os
import subprocess
import utils.utils
from Tools.rv_benchmark.tool import Tool
from utils.utils import Info
import progressbar
import signal


class TimeoutException(Exception):
    pass


class Compcert(Tool):
    def signal_handler(self, signum, frame):
        raise TimeoutException("Timed out!")

    def run(self, verbose=False, log_location=None):
        relevant_dirs = ["01.w_Defects", "02.wo_Defects"]
        for cur_dir in relevant_dirs:
            cur_path = os.path.join(self.benchmark_path, cur_dir)
            temp_path = os.path.join(cur_path, "compcert_temp")
            
            if not os.path.exists(temp_path):
                os.mkdir(temp_path)
            output_dict = {}
            spec_dict = self.info.get_spec_dict()
            mapping_dict = self.info.get_file_mapping()
            for i in range(1, 2):#len(spec_dict.keys()) + 1):
                output_dict[i] = {"count": spec_dict[i]["count"], "TP": 0, "FP": 0}
                file_prefix = mapping_dict[i]
                relevant_file = file_prefix + ".c"
                relevant_file_path = os.path.join(cur_path, relevant_file)
                if not os.path.exists(relevant_file_path):
                    continue

                print self.name + " being tested on file " + relevant_file
                #bar = progressbar.ProgressBar()
                for j in range(1, spec_dict[i]["count"]):
                    vflag = str('%03d' % j)
                    bootstrap_file_path = os.path.join(temp_path, file_prefix + "-temp.c")
                    utils.utils.bootstrap_file(relevant_file_path, bootstrap_file_path, vflag)
                    try:
                        cilly_command = ["cilly", "--merge", "--keepmerged", "--save-temps=" + temp_path,
                                         "-I" + os.path.join(self.benchmark_path, "include"),
                                         bootstrap_file_path]

                        print ' '.join(cilly_command)

                        subprocess.check_output(cilly_command)
                    except subprocess.CalledProcessError:
                        #merging of source files failed, countinue
                        continue
                    try:
                        signal.signal(signal.SIGALRM, self.signal_handler)
                        signal.alarm(10)
                        compcert_command = ["ccomp", "-interp", os.path.join(temp_path, file_prefix + "_temp.cil.c")]
                        subprocess.check_output(compcert_command)
                    except subprocess.CalledProcessError:
                        if "w_Defects" in cur_dir:
                            output_dict[i]["TP"] += 1
                        else:
                            output_dict[i]["FP"] += 1
                    except TimeoutException:
                        continue
                    finally:
                        signal.alarm(0)
            print output_dict

    def init(self):
        os.chdir(os.path.expanduser(self.benchmark_path))

    def __init__(self, benchmark_path):
        self.info = Info()
        self.benchmark_path = benchmark_path
        self.name = "Compcert"

    def analyze(self):
        Tool.analyze(self)

    def cleanup(self):
        Tool.cleanup(self)
