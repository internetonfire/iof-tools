#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import inherit_config_parser
import ConfigParser
import StringIO
from os import path
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
            self.mandatoryOptions[o] = self.getconfigurations(o, True)

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
            override_conf = StringIO.StringIO("[DEFAULT]\n" + options + "\n")
            tmp_parser = ConfigParser.ConfigParser()
            tmp_parser.optionxform = str
            tmp_parser.readfp(override_conf)
            for name, value in tmp_parser.defaults().items():
                print name, value
                self.confParams[name] = value

    def getconfigurations(self, name, raise_error=False):
        try:
            r = self.parser.get(self.testName, name)
        except ConfigParser.NoOptionError:
            if raise_error:
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

    p = Conf(path.basename(__file__), need)
    p.parseArgs()
    if not p.checkCorrectness():
        p.printUsage()
        sys.exit(1)

    configfile = p.getParam("configFile")
    testname = p.getParam("testName")

    configuration = ConfigurationFile(configfile, testname)
    # parse the conf file
    network_graph = configuration.getconfigurations("graph")
    if not network_graph:
        print("No graph topology specified in conf file or command line!")
        sys.exit(1)

    subnetter = configuration.getconfigurations("subnetting")

    graph_net = GraphNet(network_graph, subnetter)
    graph_net.setStubNodes(configuration.getconfigurations("share"))
    net = graph_net.pickGraph()
    # CLI(net)
    conf = BGPConf(configuration.confParams["dest_folder"], net, configuration.confParams)
    conf.generateFiles()
    print("*** Done with experiment: " + testname + "\n")


if __name__ == "__main__":
    generator()
