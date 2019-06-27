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

    def __init__(self, node1, node2, _type, out):
        self.node1 = node1
        self.node2 = node2
        self.type = _type
        self.outFolder = out

        # Conf files name for this edge
        self.bgpSessionFile1_name = "bgpSession_h_" + str(self.node1.name) + "_h_" + str(self.node2.name) + ".conf"
        self.bgpSessionFile2_name = "bgpSession_h_" + str(self.node2.name) + "_h_" + str(self.node1.name) + ".conf"

        # Predefined templates
        with open(BGP_SESSION_EXPORTER_TEMPLATE_PATH, "r") as bgp_file:
            self.bgp_session = bgp_file.read()
        with open(BGP_SESSION_STATIC_EXPORTER_TEMPLATE_PATH, "r") as bgp_file:
            self.bgp_session_static = bgp_file.read()

        # If this edge was not created before I need a new network, and to assign the addresses to the node interfaces
        if self.counter_external_networks < len(self.nodeIpNetworks_externalEth) and \
                (self.node1.get_external_addr(self.node2) is None and self.node2.get_external_addr(self.node1) is None):
            # Get the network
            self.edge_network = Edge.nodeIpNetworks_externalEth[Edge.counter_external_networks]
            Edge.counter_external_networks += 1
            # Assign addresses
            self.node1.set_new_external_addr(self.node2, self.edge_network[1])
            self.node2.set_new_external_addr(self.node1, self.edge_network[2])
        elif self.counter_external_networks >= len(self.nodeIpNetworks_externalEth):
            raise ValueError('No more networks available for edges')

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
        self.bgpSessionFile1 = open(self.outFolder + self.bgpSessionFile1_name, 'w+')
        self.bgpSessionFile2 = open(self.outFolder + self.bgpSessionFile2_name, 'w+')

    def __str__(self):
        return str(self.node1) + " <-> " + str(self.node2)

    # Function to export only to some nodes the information, depending on the edge type
    def write_static_exporter(self):
        node1_exported = ""
        node2_exported = ""
        if self.type == "transit":
            # I'm the customer in the edge, so if I receive something I have to send the info to only my customers
            node1_exported = self.node1.require_exported("c")
            # I'm the servicer in the edge, so if I receive something I have to send to all my connected nodes,
            # except for the customer that sent to me the info
            node2_exported = self.node2.require_exported("s", sender=self.node1)
        if self.type == "peer":
            node1_exported = self.node1.require_exported("p")
            node2_exported = self.node2.require_exported("p")

        # Write the exporter file
        self.write_session_static_exporter(self.bgpSessionFile1, "h_" + str(self.node1.name) + "_" + "h_"
                                           + str(self.node2.name), self.node1.get_external_addr(self.node2),
                                           str(int(self.node1.name) + 1), self.node2.get_external_addr(self.node1),
                                           str(int(self.node2.name) + 1), node1_exported, str(1))
        # Include the file in the node main file
        self.node1.include_in_main(self.bgpSessionFile1_name)
        if self.type != "peer":
            # Peer edges are two and I don't have to write the file at the same time
            self.write_session_static_exporter(self.bgpSessionFile2, "h_" + str(self.node2.name) + "_" + "h_"
                                               + str(self.node1.name), self.node2.get_external_addr(self.node1),
                                               str(int(self.node2.name) + 1), self.node1.get_external_addr(self.node2),
                                               str(int(self.node1.name) + 1), node2_exported, str(1))
            # Include file in the node main file
            self.node2.include_in_main(self.bgpSessionFile2_name)

    # Function to delete an exporter file
    def del_exporter(self, file_name):
        # Delete an exporter file
        if os.path.isfile(self.outFolder + file_name):
            os.remove(self.outFolder + file_name)

    # Function to write session exporters without restrictions
    def write_both_session_exporter(self):
        self.write_session_exporter(self.bgpSessionFile1, "h_" + str(self.node1.name) + "_" + "h_"
                                    + str(self.node2.name), self.node1.get_external_addr(self.node2),
                                    str(int(self.node1.name) + 1), self.node2.get_external_addr(self.node1),
                                    str(int(self.node2.name) + 1), str(1))
        self.node1.include_in_main(self.bgpSessionFile1_name)
        if self.type != "peer":
            self.write_session_exporter(self.bgpSessionFile2, "h_" + str(self.node2.name) + "_" + "h_"
                                        + str(self.node1.name), self.node2.get_external_addr(self.node1),
                                        str(int(self.node2.name) + 1), self.node1.get_external_addr(self.node2),
                                        str(int(self.node1.name) + 1), str(1))
            self.node2.include_in_main(self.bgpSessionFile2_name)

    # Write session exporter with export to all networks
    def write_session_exporter(self, file, protocol_name, local_addr, local_as, neigh_addr, neigh_as, bgp_local_pref):
        file.write(self.bgp_session.format(protocol_name=protocol_name, local_addr=local_addr,
                                           local_as=local_as, peer_addr=neigh_addr, peer_as=neigh_as,
                                           hold_timer=HOLD_TIMER,
                                           connect_retry_timer=CONNECT_RETRY_TIMER,
                                           connect_delay_timer=CONNECT_DELAY_TIMER,
                                           startup_hold_timer=STARTUP_HOLD_TIMER,
                                           local_pref=bgp_local_pref))

    # Write session exporter with a predefined export politics
    def write_session_static_exporter(self, file, protocol_name, local_addr, local_as, neigh_addr, neigh_as,
                                      export_list, bgp_local_pref):
        file.write(self.bgp_session_static.format(protocol_name=protocol_name, local_addr=local_addr,
                                                  local_as=local_as, peer_addr=neigh_addr, peer_as=neigh_as,
                                                  hold_timer=HOLD_TIMER, export_protocol=export_list,
                                                  connect_retry_timer=CONNECT_RETRY_TIMER,
                                                  connect_delay_timer=CONNECT_DELAY_TIMER,
                                                  startup_hold_timer=STARTUP_HOLD_TIMER,
                                                  local_pref=bgp_local_pref))
