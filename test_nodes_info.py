from os import mkdir
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
NODE0_NW = """
{
    "ansible_facts": {
        "ansible_default_ipv4": {
            "address": "10.2.0.216",
            "alias": "enp0s8",
            "broadcast": "10.2.15.255",
            "gateway": "10.2.15.254",
            "interface": "enp0s8",
            "macaddress": "00:30:48:78:f2:32",
            "mtu": 1500,
            "netmask": "255.255.240.0",
            "network": "10.2.0.0",
            "type": "ether"
        },
        "discovered_interpreter_python": "/usr/bin/python3"
    },
    "changed": false
}
"""
NODE1_NW = """
{
    "ansible_facts": {
        "ansible_default_ipv4": {
            "address": "10.2.0.218",
            "alias": "enp0s8",
            "broadcast": "10.2.15.255",
            "gateway": "10.2.15.254",
            "interface": "enp0s8",
            "macaddress": "00:30:48:78:f5:50",
            "mtu": 1500,
            "netmask": "255.255.240.0",
            "network": "10.2.0.0",
            "type": "ether"
        },
        "discovered_interpreter_python": "/usr/bin/python3"
    },
    "changed": false
}
"""

CPU_DIR = "cpu_info"
NW_DIR = "nw_info"


def write_temp_files(temp_dir):
    cpu_info = join(temp_dir, CPU_DIR)
    mkdir(cpu_info)
    nw_info = join(temp_dir, NW_DIR)
    mkdir(nw_info)
    n0 = open(join(cpu_info, "node0"), "w")
    n0.write(NODE0)
    n0.close()
    n1 = open(join(cpu_info, "node1"), "w")
    n1.write(NODE1)
    n1.close()
    n0 = open(join(nw_info, "node0"), "w")
    n0.write(NODE0_NW)
    n0.close()
    n1 = open(join(nw_info, "node1"), "w")
    n1.write(NODE1_NW)
    n1.close()


def test_cpu_info():
    with TemporaryDirectory() as temp_dir:
        write_temp_files(temp_dir)
        ni = NodesInfo(join(temp_dir, CPU_DIR), join(temp_dir, NW_DIR))
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


def test_nw_info():
    with TemporaryDirectory() as temp_dir:
        write_temp_files(temp_dir)
        ni = NodesInfo(join(temp_dir, CPU_DIR), join(temp_dir, NW_DIR))
        node0 = ni["node0"]
        assert(node0.nw_address == "10.2.0.216")
        assert(node0.nw_interface == "enp0s8")
        assert(node0.nw_mac == "00:30:48:78:f2:32")
        node1 = ni["node1"]
        assert(node1.nw_address == "10.2.0.218")
        assert(node1.nw_interface == "enp0s8")
        assert(node1.nw_mac == "00:30:48:78:f5:50")
        assert("node0" in ni)
        assert("node1" in ni)
        assert("node2" not in ni)
