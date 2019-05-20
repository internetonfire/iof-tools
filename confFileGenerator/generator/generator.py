#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import inherit_config_parser
import ConfigParser
import inspect
import StringIO
from os import path
from time import time
from random import seed
from parameters_parser import parameters
from BGPconfigurationMaker import BGPConf
from network_builder import *


class Conf(parameters):
    def checkCorrectness(self):
        self.checkNeededParams()
        return True


class ConfigurationFile:

    mandatoryOptions = {"graph": None, "share": None, "addrToExport": 1}
    confParams = {}
    className = None

    @staticmethod
    def file_exists(file_name):
        return path.isfile(file_name)

    def __init__(self, file_name, test_name, override_option=""):
        if not self.file_exists(file_name):
            raise "No such file or directory " + str(file_name)

        self.parser = inherit_config_parser.InheritConfigParser()
        self.parser.optionxform = str
        self.parser.read(file_name)

        self.testName = test_name

        if test_name not in self.parser.sections():
            raise "Can not find configuration " + str(test_name) + " in file " + str(file_name)

        for o in self.mandatoryOptions:
            self.mandatoryOptions[o] = self.getConfigurations(o, raiseError=True)

        graph_file = self.mandatoryOptions['graph']
        if not self.file_exists(graph_file):
            raise "No such file or directory " + str(graph_file)

        share_file = self.mandatoryOptions['share']
        if not self.file_exists(share_file):
            raise "No such file or directory " + str(share_file)

        for name, value in self.parser.items(self.testName):
            self.confParams[name] = value

        if override_option:
            options = override_option.replace(",", "\n")
            overrideConf = StringIO.StringIO("[DEFAULT]\n" + options + "\n")
            tmpParser = ConfigParser.ConfigParser()
            tmpParser.optionxform = str
            tmpParser.readfp(overrideConf)
            for name, value in tmpParser.defaults().items():
                print name, value
                self.confParams[name] = value

    def getConfigurations(self, name, raiseError=False):
        try:
            r = self.parser.get(self.testName, name)
        except ConfigParser.NoOptionError:
            if raiseError:
                raise "no option " + str(name) + " found!"
            else:
                return None
        return r


def generator():
    need = [
        ("-f", ["configFile", True, "",
         "file with the available configurations", str]),
        ("-t", ["testName", True, "",
         "base name for test output", str])
        ]

    P = Conf(path.basename(__file__), need)
    P.parseArgs()
    if not P.checkCorrectness():
        P.printUsage()
        sys.exit(1)

    configFile = P.getParam("configFile")
    testName = P.getParam("testName")
    C = ConfigurationFile(configFile, testName)
    # parse the conf file
    networkGraph = C.getConfigurations("graph")
    if not networkGraph:
        print("No graph topology specified in conf file or command line!")
        sys.exit(1)

    subnetter = C.getConfigurations("subnetting")
    graphNet = GraphNet(networkGraph, subnetter)
    graphNet.setStubNodes(C.getConfigurations("share"))
    net = graphNet.pickGraph()
    # CLI(net)
    conf = BGPConf("/", net, C.confParams)
    conf.generateFiles()
    print("*** Done with experiment: " + testName + "\n")


if __name__ == "__main__":
    generator()
