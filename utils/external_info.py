import csv
import os
from tempfile import mkstemp
from shutil import move
from os import remove, close

relevant_itc_dirs = ["01.w_defects", "02.wo_defects"]


def bootstrap_file(file_path, temp_store_file_path, vflag):
    headers = ["#include <stdio.h>", "#include <stdlib.h>", "#include <math.h>", "#include <string.h>", "#include <pthread.h>", "#include <ctype.h>", "#include <unistd.h>", "#include <limits.h>"]
    with open(temp_store_file_path, 'w+') as temp_file:
        count = 0
        main_begin = False
        with open(file_path, 'r') as cur_file:
            for line in cur_file:
                if "HeaderFile.h" in line:
                    temp_file.write("\n".join(headers))
                    temp_file.write("\n")
                    temp_file.write("extern int idx, sink;\n")
                    temp_file.write("extern double dsink;\n")
                    temp_file.write("extern void *psink;\n")
                    continue

                if "extern volatile int vflag" in line:
                    temp_file.write("int vflag = " + vflag + ";\n")
                    continue
                if "_main" in line:
                    temp_file.write("int main () \n")
                    main_begin = True
                    continue
                if main_begin:
                    if "{" in line:
                        count += 1
                    if "}" in line:
                        if count > 1:
                            count -= 1;
                        else:
                            main_begin = False
                            temp_file.write("return 0;\n")
                temp_file.write(line)


def sanitize_cil_file(file_path):
    fh, abs_path = mkstemp()
    sanitize = ["stdlib.h", "stdio.h", "math.h", "string.h", "pthread.h", "ctype.h", "unistd.h", "limits.h"]
    with open(abs_path, 'w') as new_file:
        with open(file_path) as old_file:
            extern_found = False
            for line in old_file:
                write = True
                # for word in sanitize:
                #     if word in line:
                #         write = False
                if "extern" in line:
                    extern_found = True

                if extern_found and ";" in line:
                    extern_found = False
                    continue

                if write and (not extern_found):
                    new_file.write(line)

    close(fh)
    remove(file_path)
    move(abs_path, file_path)


def checkdir(dir):
    return dir in relevant_itc_dirs



class Info:
    def __init__(self):
        __location__ = os.path.realpath(
                os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.info_csv = os.path.join(__location__, "error_info.csv")
        self.mapping_csv = os.path.join(__location__, "file_mapping.csv")
        self.ignore_file = os.path.join(__location__, "ignore_list.txt")
        self.info_dict = {}
        self.mapping = {}
        self.ignore_dict = {}
        self.ignore_list = []
        self.file_info_dict = {}
        self.count_dict = {}
        with open(self.info_csv) as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                self.info_dict[int(str(row[0]).strip())] = {"subtype": str(row[1]).strip(),
                                                            "type": str(row[2]).strip(),
                                                            "count": int(str(row[3]).strip()),
                                                            "actual_count": int(str(row[3]).strip())}

        with open(self.mapping_csv) as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                self.mapping[int(str(row[0]).strip())] = str(row[3]).strip()
                self.file_info_dict[str(row[3]).strip()] = {"number": int(str(row[0]).strip()), "type": str(row[2]).strip()}

        with open(self.ignore_file) as ignore_f:
            for line in ignore_f:
                file_name = line.split(' ')[0].strip()
                test_num = line.split(' ')[1].strip()
                file_num = self.file_info_dict[file_name]["number"]
                file_type = self.file_info_dict[file_name]["type"]
                self.ignore_list.append((int(file_num), int(test_num)))
                if file_type not in self.ignore_dict:
                    self.ignore_dict[file_type] = {"ignored": 0, "files": {}}

                if file_name not in self.ignore_dict[file_type]["files"]:
                        self.ignore_dict[file_type]["files"][file_name] = [test_num]
                else:
                    self.ignore_dict[file_type]["files"][file_name].append(test_num)

                if int(test_num) < 0:
                    self.ignore_dict[file_type]["ignored"] += self.info_dict[file_num]["count"]
                    self.info_dict[file_num]["actual_count"] = 0
                else:
                    self.ignore_dict[file_type]["ignored"] += 1
                    self.info_dict[file_num]["actual_count"] -= 1

        for key in self.info_dict:
            type = self.info_dict[key]["type"]
            actual_count = self.info_dict[key]["actual_count"]
            if type not in self.count_dict:
                self.count_dict[type] = actual_count
            else:
                self.count_dict[type] += actual_count


        self.total = 0
        for key in self.count_dict:
            self.total += self.count_dict[key]

    def get_ignore_dict(self):
        return self.ignore_dict

    def get_ignore_list(self):
        return self.ignore_list

    def get_spec_dict(self):
        return self.info_dict

    def get_file_mapping(self):
        return self.mapping

    def get_count_dict(self):
        return self.count_dict

    def get_total(self):
        return self.total