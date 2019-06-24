#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from BGP import BGP
import shutil


class BGPConf:

    def __init__(self, path_out, net, args):
        """
        Initialize function for BGPConf
        :param path_out: path where to put the confs files
        :type path_out: string
        :param net: BGP network
        :type net: networkx graph
        :param args: other args
        :type args: dictionary
        """
        self.BGP = BGP(net, path_out, args)
        self.args = args
        self.net = net
        self.prefix = args["prefix"]
        self.logPosition = str(args["log"])

    def generateFiles(self):
        """
        Function to generate the conf files
        """
        # Remove old files
        # shutil.rmtree(self.BGP.outPath)
        # Generate the path
        if not os.path.exists(self.BGP.outPath):
            os.makedirs(self.BGP.outPath)

        # Generate the log path
        if not os.path.exists(self.logPosition):
            os.makedirs(self.logPosition)

        # Get the list of hosts in order of names
        listHost = sorted(self.net.nodes(data=True), key=lambda x: x[0])

        # Set the AS of each host
        for h in listHost:
            self.BGP.setAS(h)

        # Create the exporter file for each link
        for link in self.net.edges(data=True):
            self.BGP.createExporterFile(link)

        # For each h host create the base host configuration
        for h in listHost:
            self.BGP.setBGPBaseConf(h, self.logPosition)

        # Set the configuration for the links and the comunications
        for link in self.net.edges(data=True):
            self.BGP.setBGPSession(link)

        # Copy the base files to the simulation directory
        src = "baseFiles/"
        src_files = os.listdir(src)
        for file_name in src_files:
            full_file_name = os.path.join(src, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, self.BGP.outPath)
