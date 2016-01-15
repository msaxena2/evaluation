import csv


class Info:
    def __init__(self, info_csv):
        self.info_csv = info_csv
        self.info_dict = {}
        with open(self.info_csv) as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                self.info_dict[int(str(row[0]).strip())] = {"subtype": str(row[1]).strip(),
                                                            "type": str(row[2]).strip(),
                                                            "count": int(str(row[3]).strip())}

    def get_spec_dict(self):
        return self.info_dict
