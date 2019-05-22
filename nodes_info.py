from json import load
from os import listdir
from os.path import isfile, join

FACTS = "ansible_facts"
CPU_CORES = "ansible_processor_cores"
CPU_COUNT = "ansible_processor_count"
CPU_THREADS = "ansible_processor_threads_per_core"
CPU_VCPUS = "ansible_processor_vcpus"


class NodeInfo:
    cpu_cores = 0
    cpu_count = 0
    cpu_threads = 0
    cpu_vcpus = 0

    def __init__(self, cpu_cores, cpu_count, cpu_threads, cpu_vcpus):
        self.cpu_cores = cpu_cores
        self.cpu_count = cpu_count
        self.cpu_threads = cpu_threads
        self.cpu_vcpus = cpu_vcpus


class NodesInfo:
    def __init__(self, info_dir):
        self.info_dir = info_dir
        self.nodes = {}
        self.load_info()

    def load_info(self):
        all_files = listdir(self.info_dir)
        files = [f for f in all_files if isfile(join(self.info_dir, f))]
        for f in files:
            with open(join(self.info_dir, f)) as info_file:
                json = load(info_file)
                cpu_cores = json[FACTS][CPU_CORES]
                cpu_count = json[FACTS][CPU_COUNT]
                cpu_threads = json[FACTS][CPU_THREADS]
                cpu_vcpus = json[FACTS][CPU_VCPUS]
                node = NodeInfo(cpu_cores, cpu_count, cpu_threads, cpu_vcpus)
                self.nodes[f] = node

    def __getitem__(self, item):
        return self.nodes[item]

    def __contains__(self, item):
        return item in self.nodes.keys()

    def __iter__(self):
        yield from self.nodes

    def keys(self):
        return self.nodes.keys()
