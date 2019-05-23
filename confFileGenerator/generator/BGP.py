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

from random import randint
from constants import *


class BGP:

    def __init__(self, net, out_path, args):
        """
        Init for the class BGP, used to set the local params
        :param net: Graph to use
        :type net:  networkx graph
        :param out_path: Path where will be saved the conf files
        :type out_path: String
        :param args: Other param
        :type args: dictionary
        """

        # Graph data
        self.nodes = net.nodes(data=True)
        self.links = net.edges(data=True)

        # Templates bases
        with open(BIRD_TEMPLATE_PATH, "r") as bird_file:
            self.bird_telmplate = bird_file.read()
        with open(BGP_SESSION_TEMPLATE_PATH, "r") as bgp_file:
            self.bgp_session = bgp_file.read()
        with open(BGP_SESSION_EXPORTER_TEMPLATE_PATH, "r") as bgp_file:
            self.bgp_session_exporter = bgp_file.read()
        with open(BGP_SESSION_STATIC_EXPORTER_TEMPLATE_PATH, "r") as bgp_file:
            self.bgp_session_static_exporter = bgp_file.read()

        # Addr used
        self.firstOt = 100
        self.secondOt = 1
        self.thirdOt = 1
        self.first = 200
        self.second = 0
        self.third = 0
        self.fourth = 1
        self.networkCounter = 0
        self.AsSequenceNumber = 1

        # Param retriven variables
        self.asMaxId = int(args["asMaxId"])
        self.prefix = args["prefix"]
        self.sameAsProbability = int(args["sameAsProbability"] if "sameAsProbability" in args else 0)
        self.exportProbability = args["exportProbability"] if "exportProbability" in args else 0
        self.addrToExport = int(args["addrToExport"])

        # Position where to save the conf file
        self.outPath = out_path

    def getOutPath(self):
        """
        Function to obtain the export path
        :rtype: String
        """
        return self.outPath

    def setAS(self, node):
        """
        Function to set the specific AS attribute of a node
        :param node: node object
        :type node: node by networkx graph
        """
        asNumber = str(self.AsSequenceNumber)
        if randint(1, 100) > self.sameAsProbability:
            self.AsSequenceNumber += 1
        node[1]["AS"] = asNumber
        if self.AsSequenceNumber == self.asMaxId:
            print "ERror Reached max AS length"
            self.AsSequenceNumber = 1

    def getAS(self, node_name):
        """
        Function given the node nave retrive the AS of the node
        :param node_name: Node of a node
        :type node_name: String
        :return: AS
        :rtype: String
        """
        return self.nodes[node_name]["AS"]

    # Function to get an address
    def getAddress(self):
        address = ""
        address += str(self.first) + "." + str(self.second) + "." + str(self.third) + "." + str(self.fourth)
        if self.fourth < 254:
            self.fourth += 1
        elif self.third < 254:
            self.fourth = 1
            self.third += 1
        elif self.second < 254:
            self.fourth = 1
            self.third = 1
            self.second += 1
        elif self.first < 254:
            self.fourth = 1
            self.third = 1
            self.second = 1
            self.first += 1
        else:
            print("Uable to load more addresses")
            address = ""
        return address

    # Function to get a network address
    def getNetwork(self):
        address = ""
        address += str(self.firstOt) + "." + str(self.secondOt) + "." + str(self.thirdOt) + ".0"
        if self.thirdOt < 254:
            self.thirdOt += 1
            self.networkCounter += 1
        elif self.secondOt < 254:
            self.thirdOt = 1
            self.secondOt += 1
            self.networkCounter += 1
        elif self.firstOt < 200:
            self.thirdOt = 1
            self.secondOt = 1
            self.firstOt += 1
            self.networkCounter += 1
        else:
            print("Uable to load more network address")
            address = ""
        return address

    def setBGPBaseConf(self, host, logPosition):
        """
        Function to set a basic BGP configuration
        :param host: Host that needs a configuration like basic exporter
        :type host: networkx node
        :param logPosition: where to save the logs of the bird application
        :type logPosition: String
        """
        # Variable dependent by the node
        logPath = logPosition + host[0] + ".log"
        addr = self.getAddress()
        sessionExporter = "# no bgp session exporter"

        # If the node is an exporter include the exporting file
        if host[1]["share"]:
            sessionExporter = "include  \"bgpSessionExporter_" + host[0] + "_" + self.prefix + ".conf\";"

        # Save the base file
        birdConfFile1 = self.outPath + "bird_" + host[0] + "_" + self.prefix + ".conf"

        # Crate the file
        fileBgpConf1 = open(birdConfFile1, 'w+')

        # Write the template inside the file
        fileBgpConf1.write(self.bird_telmplate.format(log_file_path=logPath, log_mode=LOG_MODE, dbg_mode=DBG_MODE,
                                                      dbg_commands_mode=DBG_COMMANDS_MODE, addr=addr,
                                                      kernel_conf_path=KERNEL_CONF_PATH,
                                                      direct_conf_path=DIRECT_CONF_PATH,
                                                      device_conf_path=DEVICE_CONF_PATH,
                                                      filter_conf_path=FILTER_CONF_PATH,
                                                      bgp_session_export_path=sessionExporter, bgp_session_path=""))

    def createExporterFile(self, link):
        """
        Function to create the exporter file given the link
        :param link: edge of the network
        :type link: Edge of networkx
        """
        # If the node 1 of the link is inside the exporters hosts i need to create the file to export a network
        if self.nodes[link[0]]["share"]:
            # Name of the protocol
            proto_name = "static_bgp_" + link[0]
            bgpFile1 = "bgpSessionExporter_" + link[0] + "_" + self.prefix + ".conf"
            # File path + file name
            bgpFilePath1 = self.outPath + bgpFile1
            # Addr to export
            addressString = ""
            # Get an addr string for each addr that need to be exported
            for i in range(self.addrToExport):
                network = self.getNetwork()
                addressString += "route " + network + "/24 via \"lo\";\n\t"

            # Open the file
            file1 = open(bgpFilePath1, 'w')
            # Write the format inside the file
            file1.write(self.bgp_session_exporter.format(session_protocol_name=proto_name,
                                                         addr_to_export=addressString))

        # The same of the node 1 for the node 2 of the link
        if self.nodes[link[1]]["share"]:
            node2Name = link[1]
            proto_name = "static_bgp_" + node2Name
            bgpFile2 = "bgpSessionExporter_" + node2Name + "_" + self.prefix + ".conf"
            bgpFilePath2 = self.outPath + bgpFile2
            addressString2 = ""
            for i in range(self.addrToExport):
                network = self.getNetwork()
                addressString2 += "route " + network + "/24 via \"lo\";"

            file2 = open(bgpFilePath2, 'w')
            file2.write(self.bgp_session_exporter.format(session_protocol_name=proto_name,
                                                         addr_to_export=addressString2))

    def findPrefBetweenNodes(self, n1, n2):
        """
        Function to find the preference between two nodes
        :param n1: Node 1
        :type n1: node
        :param n2: Node 2
        :type n2: node
        :return: Return the link
        :rtype: edge
        """
        for e in self.links:
            if e[0] == n1 and e[1] == n2:
                return e[2]["pref"]
        return None

    def confWithStaticRouteExporting(self, link):
        """
        Function to create an exporter file for a file with a pre creafted exporting protocol
        :param link: Edge where i wold like to export the network
        :type link: Edge
        :return: The protocol config string
        :rtype: String
        """
        h1 = link[0]
        h2 = link[1]

        protocol_name = h1 + h2
        local_addr = str(link[2]["addr1"]).split("/")[0]
        local_as = str(self.getAS(h1))
        neigh_addr = str(link[2]["addr2"]).split("/")[0]
        neigh_as = str(self.getAS(h2))
        bgp_local_pref = str(self.findPrefBetweenNodes(h1, h2))
        export_protocol = "static_bgp_" + h1

        return self.bgp_session_static_exporter.format(protocol_name=protocol_name, local_addr=local_addr,
                                                       local_as=local_as, peer_addr=neigh_addr, peer_as=neigh_as,
                                                       hold_timer=HOLD_TIMER, connect_retry_timer=CONNECT_RETRY_TIMER,
                                                       connect_delay_timer=CONNECT_DELAY_TIMER,
                                                       export_protocol=export_protocol,
                                                       startup_hold_timer=STARTUP_HOLD_TIMER, local_pref=bgp_local_pref)

    def confWithImportExportAll(self, link):
        """
        Function to generete an import export all configuration
        :param link: Edge where i want to export, import everythig
        :type link: networkx edge
        :return: string with the entire configuration
        :rtype: string
        """
        h1 = link[0]
        h2 = link[1]

        protocol_name = h1 + h2
        local_addr = str(link[2]["addr1"]).split("/")[0]
        local_as = str(self.getAS(h1))
        neigh_addr = str(link[2]["addr2"]).split("/")[0]
        neigh_as = str(self.getAS(h2))
        bgp_local_pref = str(self.findPrefBetweenNodes(h1, h2))

        return self.bgp_session.format(protocol_name=protocol_name, local_addr=local_addr,
                                       local_as=local_as, peer_addr=neigh_addr, peer_as=neigh_as,
                                       hold_timer=HOLD_TIMER, connect_retry_timer=CONNECT_RETRY_TIMER,
                                       connect_delay_timer=CONNECT_DELAY_TIMER,
                                       startup_hold_timer=STARTUP_HOLD_TIMER, local_pref=bgp_local_pref)

    def setBGPSession(self, link):
        """
        Function that generate a configuration given the link
        :param link: Edge between two edges that I want to insert in the conf, edges are used for the connection conf
        :type link: networkx edge
        """

        # Nodes names
        node1name = link[0]
        node2name = link[1]

        # Files to generate
        bgpFile1 = "bgpSession_" + node1name + "_" + node2name + "_" + self.prefix + ".conf"
        bgpFile2 = "bgpSession_" + node2name + "_" + node1name + "_" + self.prefix + ".conf"
        bgpFilePath1 = self.outPath + bgpFile1
        bgpFilePath2 = self.outPath + bgpFile2

        # generate the configuration with a complete import export
        bgpString1 = self.confWithImportExportAll(link)
        bgpString2 = self.confWithImportExportAll(link)

        # Write the command to iclude in the configuration
        bgpPeer1Include = "include \"" + bgpFile1 + "\";\n"
        bgpPeer2Include = "include \"" + bgpFile2 + "\";\n"

        # Open the two configurations
        file1 = open(bgpFilePath1, 'w')
        file2 = open(bgpFilePath2, 'w')

        # Write the string
        file1.write(bgpString1)
        file2.write(bgpString2)

        # Files of the base bird conf
        birdConfFile1 = self.outPath + "bird_" + link[0] + "_" + self.prefix + ".conf"
        birdConfFile2 = self.outPath + "bird_" + link[1] + "_" + self.prefix + ".conf"

        # Open them in append mode
        fileBgpConf1 = open(birdConfFile1, 'a')
        fileBgpConf2 = open(birdConfFile2, 'a')

        # Include the command for the import export
        fileBgpConf1.write(bgpPeer1Include)
        fileBgpConf2.write(bgpPeer2Include)
