from os.path import join
from tempfile import TemporaryDirectory
from nodes_info import NodesInfo


NODE0 = """
{
    "ansible_facts": {
        "ansible_processor_cores": 2,
        "ansible_processor_count": 2,
        "ansible_processor_threads_per_core": 1,
        "ansible_processor_vcpus": 4,
        "discovered_interpreter_python": "/usr/bin/python3"
    },
    "changed": false
}
"""
NODE1 = """
{
    "ansible_facts": {
        "ansible_processor_cores": 6,
        "ansible_processor_count": 2,
        "ansible_processor_threads_per_core": 2,
        "ansible_processor_vcpus": 24,
        "discovered_interpreter_python": "/usr/bin/python3"
    },
    "changed": false
}
"""


def test_nodes_info():
    with TemporaryDirectory() as temp_dir:
        n0 = open(join(temp_dir, "node0"), "w")
        n0.write(NODE0)
        n0.close()
        n1 = open(join(temp_dir, "node1"), "w")
        n1.write(NODE1)
        n1.close()
        ni = NodesInfo(temp_dir)
        node0 = ni["node0"]
        assert(node0.cpu_cores == 2)
        assert(node0.cpu_count == 2)
        assert(node0.cpu_threads == 1)
        assert(node0.cpu_vcpus == 4)
        node1 = ni["node1"]
        assert(node1.cpu_cores == 6)
        assert(node1.cpu_count == 2)
        assert(node1.cpu_threads == 2)
        assert(node1.cpu_vcpus == 24)
        assert("node0" in ni)
        assert("node1" in ni)
        assert("node2" not in ni)
