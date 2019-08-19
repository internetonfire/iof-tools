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
from constants import *
import os.path


# Class to manage edges
class Edge:
    # Class variables to manage networks
    nodeIpNetworks_externalEth = list(ipaddress.ip_network(u'10.0.0.0/12').subnets(new_prefix=30))
    counter_external_networks = 0

    def __init__(self, node1, node2, _type, addresses, out1, out2):
        if len(addresses) != 2:
            raise exception('invalid addresses parameter, addresses is a list of exactly two str ips')

        self.node1 = node1
        self.node2 = node2
        if addresses[0] != "" and addresses[1] != "":
            self.node1Eth = ipaddress.IPv4Interface(addresses[0])
            self.node2Eth = ipaddress.IPv4Interface(addresses[1])

            if self.node1Eth.network != self.node2Eth.network:
                raise Exception('invalid addresses parameter, addresses needs to belong to the same network')
            if self.node1Eth.netmask != self.node2Eth.netmask or int(self.node1Eth.netmask) != 4294967292:
                raise Exception('invalid addresses parameter, addresses needs to belong to a /30 network')

            self.edge_network = self.node1Eth.network
            self.node1.set_new_external_addr(self.node2, self.node1Eth.ip)
            self.node2.set_new_external_addr(self.node1, self.node2Eth.ip)
        else:
            # If this edge was not created before I need a new network, and to assign the addresses
            # to the node interfaces
            if self.counter_external_networks < len(self.nodeIpNetworks_externalEth) and \
                    (self.node1.get_external_addr(self.node2) is None and self.node2.get_external_addr(
                        self.node1) is None):
                # Get the network
                self.edge_network = Edge.nodeIpNetworks_externalEth[Edge.counter_external_networks]
                Edge.counter_external_networks += 1
                # Assign addresses
                self.node1.set_new_external_addr(self.node2, self.edge_network[1])
                self.node2.set_new_external_addr(self.node1, self.edge_network[2])
            elif self.counter_external_networks >= len(self.nodeIpNetworks_externalEth):
                raise ValueError('No more networks available for edges')
        self.type = _type
        self.outFolder1 = out1
        self.outFolder2 = out2

        # Conf files name for this edge
        self.bgpSessionFile1_name = "bgpSession_h_" + str(self.node1.name) + "_h_" + str(self.node2.name) + ".conf"
        self.bgpSessionFile2_name = "bgpSession_h_" + str(self.node2.name) + "_h_" + str(self.node1.name) + ".conf"

        # Predefined templates
        with open(BGP_SESSION_EXPORTER_TEMPLATE_PATH, "r") as bgp_file:
            self.bgp_session = bgp_file.read()
        with open(BGP_SESSION_STATIC_EXPORTER_TEMPLATE_PATH_UPLINKS, "r") as bgp_file:
            self.bgp_session_static_uplinks = bgp_file.read()
        with open(BGP_SESSION_STATIC_EXPORTER_TEMPLATE_PATH_PEERS, "r") as bgp_file:
            self.bgp_session_static_peers = bgp_file.read()
        with open(BGP_SESSION_STATIC_EXPORTER_TEMPLATE_PATH_CLIENTS, "r") as bgp_file:
            self.bgp_session_static_clients = bgp_file.read()

        # Add the node to the node set depending on the edge type
        if self.type == "transit":
            self.node1.add_servicer(self.node2)
            self.node2.add_customer(self.node1)
        elif self.type == "peer":
            self.node1.add_peer(self.node2)
            self.node2.add_peer(self.node1)
        else:
            raise ValueError("Type not correct, it's possible to use only transit and peer")

        # Open the files for the edge
        self.bgpSessionFile1 = open(self.outFolder1 + self.bgpSessionFile1_name, 'w+')
        self.bgpSessionFile2 = open(self.outFolder2 + self.bgpSessionFile2_name, 'w+')

    def __str__(self):
        return str(self.node1) + " <-> " + str(self.node2)

    # Function to export only to some nodes the information, depending on the edge type
    def write_static_exporter(self):
        lst = self.node1.get_customers_addresses()
        client_list = ""
        if len(lst) > 0:
            client_list = "return bgp_next_hop ~ " + str(lst).replace("'", "") + ";"

        lst = self.node2.get_customers_addresses()
        client_list2 = ""
        if len(lst) > 0:
            client_list2 = "return bgp_next_hop ~ " + str(lst).replace("'", "") + ";"

        if self.type == "transit":
            # Write the exporter file
            self.write_session_static_exporter_uplinks(self.bgpSessionFile1, str(client_list), "h_" +
                                                       str(self.node1.name) + "_" + "h_" + str(self.node2.name),
                                                       self.node1.get_external_addr(self.node2),
                                                       str(int(self.node1.name) + 1),
                                                       self.node2.get_external_addr(self.node1),
                                                       str(int(self.node2.name) + 1), self.node1.mrai, str(1))
            # Include the file in the node main file
            self.node1.include_in_main(self.bgpSessionFile1_name)
            self.write_session_static_exporter_clients(self.bgpSessionFile2, "h_" + str(self.node2.name) + "_" + "h_"
                                                       + str(self.node1.name), self.node2.get_external_addr(self.node1),
                                                       str(int(self.node2.name) + 1),
                                                       self.node1.get_external_addr(self.node2),
                                                       str(int(self.node1.name) + 1), self.node2.mrai, str(1))
            # Include file in the node main file
            self.node2.include_in_main(self.bgpSessionFile2_name)
        if self.type == "peer":
            # Write the exporter file
            self.write_session_static_exporter_peers(self.bgpSessionFile1, str(client_list), "h_" + str(self.node1.name)
                                                     + "_" + "h_" + str(self.node2.name),
                                                     self.node1.get_external_addr(self.node2),
                                                     str(int(self.node1.name) + 1),
                                                     self.node2.get_external_addr(self.node1),
                                                     str(int(self.node2.name) + 1), self.node1.mrai, str(1))
            # Include the file in the node main file
            self.node1.include_in_main(self.bgpSessionFile1_name)
            self.write_session_static_exporter_peers(self.bgpSessionFile2, str(client_list2), "h_" + str(self.node2.name)
                                                     + "_" + "h_" + str(self.node1.name),
                                                     self.node2.get_external_addr(self.node1),
                                                     str(int(self.node2.name) + 1),
                                                     self.node1.get_external_addr(self.node2),
                                                     str(int(self.node1.name) + 1), self.node2.mrai, str(1))
            # Include the file in the node main file
            self.node2.include_in_main(self.bgpSessionFile2_name)

    # Write session exporter with a predefined export politics
    def write_session_static_exporter_uplinks(self, file, clients_list, protocol_name, local_addr, local_as, neigh_addr,
                                              neigh_as, mrai, bgp_local_pref):
        file.write(self.bgp_session_static_uplinks.format(rt_export_name="rt_export_" + protocol_name,
                                                          client_list=clients_list, filter_in_name="filter_in_" +
                                                          protocol_name, filter_out_name="filter_out_" + protocol_name,
                                                          peer_as_filter=neigh_as, protocol_name=protocol_name,
                                                          local_addr=local_addr, local_as=local_as,
                                                          peer_addr=neigh_addr, peer_as=neigh_as, hold_timer=HOLD_TIMER,
                                                          mrai_timer=mrai, connect_retry_timer=CONNECT_RETRY_TIMER,
                                                          connect_delay_timer=CONNECT_DELAY_TIMER,
                                                          startup_hold_timer=STARTUP_HOLD_TIMER,
                                                          local_pref=bgp_local_pref))

    def write_session_static_exporter_peers(self, file, clients_list, protocol_name, local_addr, local_as, neigh_addr,
                                            neigh_as, mrai, bgp_local_pref):
        file.write(self.bgp_session_static_peers.format(rt_export_name="rt_export_" + protocol_name,
                                                        client_list=clients_list, filter_in_name="filter_in_" +
                                                        protocol_name, filter_out_name="filter_out_" + protocol_name,
                                                        peer_as_filter=neigh_as, protocol_name=protocol_name,
                                                        local_addr=local_addr, local_as=local_as, peer_addr=neigh_addr,
                                                        peer_as=neigh_as, hold_timer=HOLD_TIMER, mrai_timer=mrai,
                                                        connect_retry_timer=CONNECT_RETRY_TIMER,
                                                        connect_delay_timer=CONNECT_DELAY_TIMER,
                                                        startup_hold_timer=STARTUP_HOLD_TIMER,
                                                        local_pref=bgp_local_pref))

    def write_session_static_exporter_clients(self, file, protocol_name, local_addr, local_as, neigh_addr, neigh_as,
                                              mrai, bgp_local_pref):
        file.write(self.bgp_session_static_clients.format(filter_in_name="filter_in_" + protocol_name,
                                                          filter_out_name="filter_out_" + protocol_name,
                                                          peer_as_filter=neigh_as, protocol_name=protocol_name,
                                                          local_addr=local_addr, local_as=local_as,
                                                          peer_addr=neigh_addr, peer_as=neigh_as, hold_timer=HOLD_TIMER,
                                                          mrai_timer=mrai, connect_retry_timer=CONNECT_RETRY_TIMER,
                                                          connect_delay_timer=CONNECT_DELAY_TIMER,
                                                          startup_hold_timer=STARTUP_HOLD_TIMER,
                                                          local_pref=bgp_local_pref))
