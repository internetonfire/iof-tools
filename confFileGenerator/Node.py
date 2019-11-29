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
# TODO usage of import * is discuraged
from constants import *
import os.path
from jinja2 import Environment, FileSystemLoader


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

    def __init__(self, node, out_folder, variables):
        """
        Class node initializer, this class is used to control bird configuration nodes
        :param node: the node from networkx that you want to transform in a bird conf
        :param out_folder: the output folder where to save the configuration of this node
        """

        if 'type' not in node[1]:
            raise ValueError("No type in node, this arg is mandatory")

        self.name = node[0]
        self.type = node[1]['type']
        self.outFolder = out_folder

        self.variables = variables

        self.ipNetworksToShare = ""
        if self.variables.ipNetworks in node[1]:
            self.ipNetworksToShare = node[1][variables.ipNetworks].split(',')

        # Major output file
        self.mainOutFileName = "bgp_h_" + str(self.name) + ".conf"
        # Session exporter file
        self.sessionExporterFile_name = "bgpSessionExporter_h_" + str(self.name) + ".conf"

        # Obtain the router id address
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
        with open(MRAI_TEMPLATE_FILE, "r") as mrai_file:
            self.mrai_template = mrai_file.read()

        self.mainOutFile = open(self.outFolder + self.mainOutFileName, 'w+')
        self.sessionExporterFile = None
        self.exporting_proto_name = "static_bgp"
        self.exportedNetworks = []
        self.exportedNetworks_str = ""
        self.log_file_name = "log_h_" + str(self.name) + ".log"
        self.network_file_name = "network-config-node-" + str(self.name) + ".sh"

        self.eth_dict = {}
        self.customer = {}
        self.peer = {}
        self.servicer = {}

        self.write_main_file()

    def __str__(self):
        return "{" + str(self.name) + "," + str(self.router_addr) + "}"

    def add_customer(self, node):
        """
        Function used to append a new customer node to this node customers dictionary
        :param node: node object to append
        """
        self.customer[node.name] = node

    def add_peer(self, node):
        """
        Function used to append a new peer node to this node peer dictionary
        :param node: node object to append
        """
        self.peer[node.name] = node

    def add_servicer(self, node):
        """
        Function used to append a new servicer node to this node servicer dictionary
        :param node: node object to append
        """
        self.servicer[node.name] = node

    def get_customers_addresses(self):
        """
        Function userd to get the list of all customers ips
        :return: list of strings
        """
        addr_list = []
        for node in self.customer.values():
            addr_list.append(str(node.get_external_addr(self)))
        return addr_list

    def add_addr_to_export(self, ip_networks_to_share=""):
        """
        Function used to append a new network address to share
        No checks will be done on the address, only if it's a valid network address
        :param ip_networks_to_share: this is an optional param that could be used to set manually the networks that
                                     has to be shared
        """
        if Node.counter_networks < len(Node.nodeIpNetworks_network) and ip_networks_to_share == "":
            # Automatic chose of the network address
            self.exportedNetworks.append(Node.nodeIpNetworks_network[Node.counter_networks])
            Node.counter_networks += 1
        elif ip_networks_to_share != "":
            # manual chose of the network address
            network = ipaddress.ip_network(ip_networks_to_share)
            self.exportedNetworks.append(network)
        else:
            raise ValueError('No more networks free')

        # Append the route
        self.exportedNetworks_str += "route " + str(self.exportedNetworks[-1]) + " via \"lo\";\n\t\t\t\t\t\t"

        self.write_export_file()

    def write_main_file(self):
        # Write the template inside the file
        open(self.outFolder + self.log_file_name, "a").close()
        self.mainOutFile.write(
            self.bird_template.format(log_file_path=self.variables.PREPATH+self.log_file_name,
                                      log_mode=self.variables.log_mode, dbg_mode=DBG_MODE,
                                      dbg_commands_mode=DBG_COMMANDS_MODE, addr=self.router_addr,
                                      kernel_conf_path=self.variables.PREPATH + KERNEL_CONF_PATH,
                                      direct_conf_path=self.variables.PREPATH + DIRECT_CONF_PATH,
                                      device_conf_path=self.variables.PREPATH + DEVICE_CONF_PATH,
                                      filter_conf_path=self.variables.PREPATH + FILTER_CONF_PATH,
                                      bgp_session_export_path="", bgp_session_path=""))

    def write_network_configuration(self):
        # Write the network configuration of the node
        env = Environment(loader=FileSystemLoader('templates/'))
        baseline = env.get_template(NETWORK_TEMPLATE_PATH)
        ip_addresses = []
        for _, ip in self.eth_dict.items():
            ip_addresses.append(str(ip))
        rendered_template = baseline.render(name=self.name, ipaddresses=ip_addresses)
        with open(self.outFolder + self.network_file_name, "w") as netfd:
            netfd.write(rendered_template)

    def delete_export_file(self):
        if os.path.isfile(self.outFolder + self.sessionExporterFile_name):
            os.remove(self.outFolder + self.sessionExporterFile_name)

    def write_export_file(self):
        self.sessionExporterFile = open(self.outFolder + self.sessionExporterFile_name, "w+")
        self.sessionExporterFile.write(self.bgp_session_exporter.format(session_protocol_name=self.exporting_proto_name,
                                                                        addr_to_export=self.exportedNetworks_str))

    def include_in_main(self, file_name):
        self.mainOutFile.write("include  \"" + self.variables.PREPATH + file_name + "\";\n")

    def set_new_external_addr(self, neighbor_node, addr):
        self.eth_dict[str(neighbor_node.name)] = addr

    def get_external_addr(self, neighbor_node):
        if str(neighbor_node.name) in self.eth_dict.keys():
            return self.eth_dict[str(neighbor_node.name)]
        return None

    def install_networks(self):
        """
        Function used to install all the predefined networks inside the node, if networks are not predefined
        A predefined networks pool will be used, only if this is not denied by an explicit command
        """
        if set(self.type).issubset(SHARINGSET):
            if len(self.ipNetworksToShare) >= 1:
                for net in self.ipNetworksToShare:
                    self.add_addr_to_export(net)
                self.include_in_main(self.sessionExporterFile_name)
            elif self.variables.networks and len(self.ipNetworksToShare) == 0:
                self.add_addr_to_export()
                self.include_in_main(self.sessionExporterFile_name)
