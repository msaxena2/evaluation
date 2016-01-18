__author__ = 'manasvi'
class Tool:

    def __init__(self):
        pass
    def run(self):
        pass

    def get_tool_name(self):
        pass

    def cleanup(self):
        pass

    def get_errors(self):
        pass

    def get_numbers(self):
        pass

    def get_error_code(self, c_file):
        if "-good" in c_file:
            error_code = c_file.split("-good")[0]
        else:
            error_code = c_file.split("-bad")[0]
        return error_code


    def print_folder(self, name, folder):
        print name + " testing folder " + folder

