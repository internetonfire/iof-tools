#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
#
# Copyright (C) 2019  Mattia Milani <mattia.milani@studenti.unitn.it>

import ipaddress
from os.path import join

from constants import *
import os.path


BRIDGE = "br-iof"
BRIDGE_CONF = """
exists=`brctl show | grep {bridge}`
if [ -z "$exists" ]; then
    brctl addbr {bridge}
fi
brctl stp   {bridge} off
ip link set dev {bridge} up
""".format(bridge=BRIDGE)

NS_CONF = """
ip netns add ns{host}
ip netns exec ns{host} ip link set lo up
"""

TAP_CONF = """
# create a port pair
ip link add tap{host} type veth peer name br-tap{host}
# attach one side to linuxbridge
brctl addif {bridge} br-tap{host}
# attach the other side to namespace
ip link set tap{host} netns ns{host}
# set the ports to up
ip netns exec ns{host} ip link set dev tap{host} up
ip link set dev br-tap{host} up
"""

IP_CONF = """
ip netns exec ns{host} ip addr add {ip}/30 dev tap{host}
"""

IF_BRIDGE = """
ip link set {interface} up
brctl addif {bridge} {interface}
"""


class Node:
    nodeIpAddr_network = ipaddress.ip_network(u'200.0.0.0/8')
    counter_node = 1
    # ATTENTION if you would like to change the network 100.0.0.0/8 also change it in the conf file commonFilters.conf
    # otherwise the configuration probably would drop all update packets.
    nodeIpNetworks_network = list(ipaddress.ip_network(u'100.0.0.0/8').subnets(new_prefix=24))
    counter_networks = 1
    ClientList = []

    def __init__(self, name, node_type, out_folder, mrai='0',
                 interface="enp0s9"):
        self.name = name
        self.type = node_type
        self.mrai = int(float(mrai)*1000)
        self.intf = interface

        if self.type == "C":
            Node.ClientList.append(int(self.name)+1)

        self.outFolder = out_folder
        self.mainOutFileName = "bgp_h_" + str(self.name) + ".conf"
        self.sessionExporterFile_name = "bgpSessionExporter_h_" + str(name) + ".conf"
        if Node.counter_node < Node.nodeIpAddr_network.num_addresses - 1:
            self.router_addr = Node.nodeIpAddr_network[Node.counter_node]
            Node.counter_node += 1
        else:
            raise ValueError('No more addresses for routers')

        # Templates bases
        with open(BIRD_TEMPLATE_PATH, "r") as bird_file:
            self.bird_template = bird_file.read()
        with open(BGP_SESSION_EXPORTER_TEMPLATE_PATH, "r") as bgp_file:
            self.bgp_session_exporter = bgp_file.read()

        self.mainOutFile = open(self.outFolder + self.mainOutFileName, 'w+')
        self.sessionExporterFile = None
        self.exporting_proto_name = "static_bgp"
        self.exportedNetworks = []
        self.exportedNetworks_str = ""
        self.log_file_name = "log_h_" + str(self.name) + ".log"

        self.eth_dict = {}
        self.customer = {}
        self.peer = {}
        self.servicer = {}

        self.write_main_file()

    def __str__(self):
        return "{" + str(self.name) + "," + str(self.router_addr) + "}"

    def add_customer(self, node):
        self.customer[node.name] = node

    def add_peer(self, node):
        self.peer[node.name] = node

    def add_servicer(self, node):
        self.servicer[node.name] = node

    def get_customers_addresses(self):
        addr_list = []
        for node in self.customer.values():
            addr_list.append(str(node.get_external_addr(self)))
        return addr_list

    def add_addr_to_export(self):
        if Node.counter_networks < len(Node.nodeIpNetworks_network):
            self.exportedNetworks.append(Node.nodeIpNetworks_network[Node.counter_networks])
            Node.counter_networks += 1
        else:
            raise ValueError('No more networks free')
        self.delete_export_file()

        self.exportedNetworks_str += "route " + str(self.exportedNetworks[-1]) + " via \"lo\";\n\t\t\t"

        self.write_export_file()
        self.include_in_main(self.sessionExporterFile_name)

    def write_main_file(self):
        # Write the template inside the file
        open(self.outFolder + self.log_file_name, "a").close()
        self.mainOutFile.write(
            self.bird_template.format(log_file_path="./"+self.log_file_name, log_mode=LOG_MODE,
                                      dbg_mode=DBG_MODE, dbg_commands_mode=DBG_COMMANDS_MODE, addr=self.router_addr,
                                      kernel_conf_path=KERNEL_CONF_PATH,
                                      direct_conf_path=DIRECT_CONF_PATH,
                                      device_conf_path=DEVICE_CONF_PATH,
                                      filter_conf_path=FILTER_CONF_PATH,
                                      bgp_session_export_path="", bgp_session_path=""))

    def write_network_configuration(self):
        host = self.name
        output = "{}_conf.sh".format(host)
        # TODO: before this: assign this AS to one testbed node
        # TODO: read interface name from device configuration
        with open(join(self.outFolder, output), "w") as out_file:
            out_file.write(BRIDGE_CONF)
            out_file.write(NS_CONF.format(host=host))
            out_file.write(TAP_CONF.format(host=host, bridge=BRIDGE))
            out_file.write(IF_BRIDGE.format(bridge=BRIDGE, interface=self.intf))
            for _,ip in self.eth_dict.items():
                out_file.write(IP_CONF.format(host=host, ip=str(ip)))

    def delete_export_file(self):
        if os.path.isfile(self.outFolder + self.sessionExporterFile_name):
            os.remove(self.outFolder + self.sessionExporterFile_name)

    def write_export_file(self):
        self.sessionExporterFile = open(self.outFolder + self.sessionExporterFile_name, "w+")
        self.sessionExporterFile.write(self.bgp_session_exporter.format(session_protocol_name=self.exporting_proto_name,
                                                                        addr_to_export=self.exportedNetworks_str))

    def include_in_main(self, file_name):
        self.mainOutFile.write("include  \"./" + file_name + "\";\n")

    def set_new_external_addr(self, neighbor_node, addr):
        self.eth_dict[str(neighbor_node.name)] = addr

    def get_external_addr(self, neighbor_node):
        if str(neighbor_node.name) in self.eth_dict.keys():
            return self.eth_dict[str(neighbor_node.name)]
        return None
