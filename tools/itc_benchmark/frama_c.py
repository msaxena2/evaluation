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
import pickle

class TimeoutException(Exception):
    pass


class FramaC(Tool):
    def signal_handler(self, signum, frame):
        raise TimeoutException("Timed out!")

    def analyze_output(self, output, file_name):
        print output
        for line in output.split('\n'):
            if file_name in line and "WARNING" in line.upper():
                if "Neither code nor specification" in line:
                    continue
                # Simple condition for an alarm in the file
                return True
        return False

    def pickle_set(self, tp_set, fp_set, tp_file, fp_file):
        with open(tp_file, 'w+') as tp:
            pickle.dump(tp_set, tp)
        with open(fp_file, 'w+') as fp:
            pickle.dump(fp_set, fp)

    def sanitize_header_file(self, original_header_path, new_header_path, framac_include_path, header_file_name):
        allowed_list = map(lambda z : z.split('/')[-1], [y for x in os.walk(framac_include_path) for y in glob(os.path.join(x[0], '*.h'))])
        pattern = re.compile('#include\ *<(.*)>')
        if not os.path.exists(new_header_path):
            os.mkdir(new_header_path)
        with open(os.path.join(new_header_path, header_file_name), 'w+') as temp_file:
            with open(os.path.join(original_header_path, header_file_name), 'r') as cur_file:
                for line in cur_file:
                    match = re.match(pattern, line)
                    if match:
                        if match.group(1) not in allowed_list:
                            continue
                    temp_file.write(line)


    def get_framac_command(self, cur_dir, file_prefix, temp_dir_name, vflag):
        cur_path = os.path.join(self.benchmark_path, cur_dir)
        temp_path = os.path.join(cur_path, temp_dir_name)
        if not os.path.exists(temp_path):
            os.mkdir(temp_path)

        relevant_file_path = os.path.join(cur_path, file_prefix + ".c")
        bootstrap_file_path = os.path.join(temp_path, file_prefix + "-temp.c")
        utils.external_info.bootstrap_file(relevant_file_path, bootstrap_file_path, vflag)
        return ["frama-c", "-val", bootstrap_file_path]

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
                        framac_command = self.get_framac_command(cur_dir, file_prefix, "framac_dir", vflag)
                        print " ".join(framac_command)
                        if len(framac_command) != 0:
                            signal.signal(signal.SIGALRM, self.signal_handler)
                            #signal.alarm(10)
                            output = subprocess.check_output(framac_command, stderr=subprocess.STDOUT)
                            print output
                            verdict = self.analyze_output(output, file_prefix)
                            if verdict:
                                if "w_Defects" in cur_dir:
                                    output_dict[i]["TP"] += 1
                                else:
                                    output_dict[i]["FP"] += 1

                    except subprocess.CalledProcessError as e:
                        signal.alarm(0)
                        #error with the plugin
                        continue

                    except TimeoutException:
                        continue
                    finally:
                        if verdict:
                            self.logger.log_output(output, file_prefix + ".c", cur_dir, str(j), "TP")
                        if not verdict:
                            self.logger.log_output(output, file_prefix + ".c", cur_dir, str(j), "NEG")
                        signal.alarm(0)
        return output_dict

    def get_name(self):
        return self.name

    def __init__(self, benchmark_path, log_path):
        self.info = Info()
        self.benchmark_path = benchmark_path
        self.name = "framac"
        self.logger = Logger(log_path, self.name)
        self.fp_set = set()
        self.tp_set = set()

    def analyze(self):
        Tool.analyze(self)

    def cleanup(self):
        Tool.cleanup(self)
        self.logger.close_log()
