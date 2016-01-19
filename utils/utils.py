import csv
import os
relevant_itc_dirs = ["01.w_defects", "02.wo_defects"]


class Info:
    def __init__(self):
        __location__ = os.path.realpath(
                os.path.join(os.getcwd(), os.path.dirname(__file__)))
        self.info_csv = os.path.join(__location__, "error_info.csv")
        self.mapping_csv = os.path.join(__location__, "file_mapping.csv")
        self.info_dict = {}
        self.mapping = {}
        with open(self.info_csv) as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                self.info_dict[int(str(row[0]).strip())] = {"subtype": str(row[1]).strip(),
                                                            "type": str(row[2]).strip(),
                                                            "count": int(str(row[3]).strip())}

        with open(self.mapping_csv) as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                self.mapping[int(str(row[0]).strip())] = str(row[3]).strip()

    def get_spec_dict(self):
        return self.info_dict

    def get_file_mapping(self):
        return self.mapping


def bootstrap_file(file_path, temp_store_file_path, vflag):
    with open(temp_store_file_path, 'w+') as temp_file:
        count = 0
        main_begin = False
        with open(file_path, 'r') as cur_file:
            for line in cur_file:
                if "extern volatile int vflag" in line:
                    temp_file.write("int vflag = " + vflag+";\n")
                    continue
                if "_main" in line:
                    temp_file.write("int idx, sink;\n")
                    temp_file.write("double dsink;\n")
                    temp_file.write("void * psipk;\n")
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


def checkdir(dir):
    return dir in relevant_itc_dirs
