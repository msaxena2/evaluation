__author__ = 'manasvi'
from utils import Info
class Tool:

    def __init__(self, benchmark_location):
        self.input_file = benchmark_location

    def init(self):
        pass

    def run(self):
        pass

    def analyze(self):
        pass

    def cleanup(self):
        pass

if __name__ == '__main__':
    info = Info("utils.csv")
    info.get_spec_dict()

