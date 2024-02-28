#==============================================================================
# Copyright (C) 2019-2024 Mattia Milani, Leonardo Maccari, Luca Baldesi, Lorenzo Ghiro, Michele Segata, Marco Nesler 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#==============================================================================
from json import load
from os import listdir
from os.path import isfile, join

FACTS = "ansible_facts"
CPU_CORES = "ansible_processor_cores"
CPU_COUNT = "ansible_processor_count"
CPU_THREADS = "ansible_processor_threads_per_core"
CPU_VCPUS = "ansible_processor_vcpus"
NW_IPV4 = "ansible_default_ipv4"
NW_ADDRESS = "address"
NW_INTERFACE = "interface"
NW_MAC = "macaddress"


class NodeInfo:
    cpu_cores = 0
    cpu_count = 0
    cpu_threads = 0
    cpu_vcpus = 0
    nw_address = ""
    nw_interface = ""
    nw_mac = ""

    def __init__(self, cpu_cores=0, cpu_count=0, cpu_threads=0, cpu_vcpus=0,
                 nw_address="", nw_interface="", nw_mac=""):
        self.cpu_cores = cpu_cores
        self.cpu_count = cpu_count
        self.cpu_threads = cpu_threads
        self.cpu_vcpus = cpu_vcpus
        self.nw_address = nw_address
        self.nw_interface = nw_interface
        self.nw_mac = nw_mac

    def set_cpu_info(self, cpu_cores, cpu_count, cpu_threads, cpu_vcpus):
        self.cpu_cores = cpu_cores
        self.cpu_count = cpu_count
        self.cpu_threads = cpu_threads
        self.cpu_vcpus = cpu_vcpus

    def set_nw_info(self, nw_address, nw_interface, nw_mac):
        self.nw_address = nw_address
        self.nw_interface = nw_interface
        self.nw_mac = nw_mac


class NodesInfo:
    def __init__(self, cpu_dir, nw_dir):
        self.cpu_dir = cpu_dir
        self.nw_dir = nw_dir
        self.nodes = {}
        self.load_cpu_info()
        self.load_nw_info()

    def load_cpu_info(self):
        all_files = listdir(self.cpu_dir)
        files = [f for f in all_files if isfile(join(self.cpu_dir, f))]
        for f in files:
            with open(join(self.cpu_dir, f)) as info_file:
                json = load(info_file)
                cpu_cores = json[FACTS][CPU_CORES]
                cpu_count = json[FACTS][CPU_COUNT]
                cpu_threads = json[FACTS][CPU_THREADS]
                cpu_vcpus = json[FACTS][CPU_VCPUS]
                if f in self.nodes.keys():
                    self.nodes[f].set_cpu_info(cpu_cores, cpu_count,
                                               cpu_threads, cpu_vcpus)
                else:
                    node = NodeInfo(cpu_cores, cpu_count, cpu_threads,
                                    cpu_vcpus)
                    self.nodes[f] = node

    def load_nw_info(self):
        all_files = listdir(self.nw_dir)
        files = [f for f in all_files if isfile(join(self.nw_dir, f))]
        for f in files:
            with open(join(self.nw_dir, f)) as info_file:
                json = load(info_file)
                nw_address = json[FACTS][NW_IPV4][NW_ADDRESS]
                nw_interface = json[FACTS][NW_IPV4][NW_INTERFACE]
                nw_mac = json[FACTS][NW_IPV4][NW_MAC]
                if f in self.nodes.keys():
                    self.nodes[f].set_nw_info(nw_address, nw_interface, nw_mac)
                else:
                    node = NodeInfo(nw_address=nw_address,
                                    nw_interface=nw_interface, nw_mac=nw_mac)
                    self.nodes[f] = node

    def __getitem__(self, item):
        return self.nodes[item]

    def __contains__(self, item):
        return item in self.nodes.keys()

    def __iter__(self):
        yield from self.nodes

    def keys(self):
        return self.nodes.keys()
