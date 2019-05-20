#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from recordtype import recordtype
from network_builder import *
from random import randint
import glob
import re
from datetime import datetime
from BGP import BGP
import shutil

class BGPConf():

    def __init__(self, path_out, net, args):
        self.BGP = BGP(net, path_out, args)
        self.args = args
        self.net = net
        self.prefix = args["prefix"]
        self.logPosition = str(args["log"])

    def generateFiles(self):
        print self.BGP.outPath
        if not os.path.exists(self.BGP.outPath):
            os.makedirs(self.BGP.outPath)

        if not os.path.exists(self.logPosition):
            os.makedirs(self.logPosition)

        self.BGP.setPrefix(self.prefix)

        listHost = sorted(self.net.nodes(data=True), key=lambda x: x[0])

        for h in listHost:
            self.BGP.setAS(h)

        for link in self.net.edges(data=True):
            self.BGP.createExporterFile(link, self.prefix)

        for h in listHost:
            self.BGP.setBGPBaseConf(h, self.logPosition, self.prefix)

        for link in self.net.edges(data=True):
            self.BGP.setBGPSession(link, self.prefix)

        src = "baseFiles/"
        src_files = os.listdir(src)
        for file_name in src_files:
            full_file_name = os.path.join(src, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, self.BGP.outPath)
