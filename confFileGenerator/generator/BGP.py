#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import randint
from constants import *


class BGP:

    def __init__(self, net, name, args):
        self.name = name
        self.prefix = ""
        self.nodes = net.nodes(data=True)
        self.links = net.edges(data=True)

        with open(BIRD_TEMPLATE_PATH, "r") as bird_file:
            self.bird_telmplate = bird_file.read()
        with open(BGP_SESSION_TEMPLATE_PATH, "r") as bgp_file:
            self.bgp_session = bgp_file.read()
        with open(BGP_SESSION_EXPORTER_TEMPLATE_PATH, "r") as bgp_file:
            self.bgp_session_exporter = bgp_file.read()

        self.firstOt = 100
        self.secondOt = 1
        self.thirdOt = 1
        self.first = 200
        self.second = 0
        self.third = 0
        self.fourth = 1
        self.networkCounter = 0
        self.AsSequenceNumber = 1

        self.asMaxId = int(args["asMaxId"])
        self.sameAsProbability = int(args["sameAsProbability"] if "sameAsProbability" in args else 0)

        spl = args["share"].split("/")
        spl[-1] = spl[-1].rstrip(".stub")
        self.outPath = ("/".join(spl[:-1]) + "/conf/")

        self.exportProbability = args["exportProbability"] if "exportProbability" in args else 0
        self.addrToExport = int(args["addrToExport"])

    def getOutPath(self):
        return self.outPath

    def setPrefix(self, prefix):
        self.prefix = prefix

    def resetAS(self):
        self.AsSequenceNumber = 1

    def setAS(self, node):
        asNumber = str(self.AsSequenceNumber)
        if randint(1, 100) > self.sameAsProbability:
            self.AsSequenceNumber += 1

        node[1]["AS"] = asNumber

        if self.AsSequenceNumber == self.asMaxId:
            self.AsSequenceNumber = 1

    def getAS(self, node_name):
        return self.nodes[node_name]["AS"]

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

    def setBGPBaseConf(self, host, logPosition, simulationADR):
        logPath = logPosition + host[0]
        addr = self.getAddress()
        sessionExporter = "# no bgp session exporter"

        if host[1]["share"]:
            sessionExporter = "include  \"bgpSessionExporter_" + host[0] + "_" + simulationADR + ".conf\";"

        birdConfFile1 = self.outPath + "bird_" + host[0] + "_" + simulationADR + ".conf"

        fileBgpConf1 = open(birdConfFile1, 'w+')

        fileBgpConf1.write(self.bird_telmplate.format(log_file_path=logPath, log_mode=LOG_MODE, dbg_mode=DBG_MODE,
                                                      dbg_commands_mode=DBG_COMMANDS_MODE, addr=addr,
                                                      kernel_conf_path=KERNEL_CONF_PATH,
                                                      direct_conf_path=DIRECT_CONF_PATH,
                                                      device_conf_path=DEVICE_CONF_PATH,
                                                      filter_conf_path=FILTER_CONF_PATH,
                                                      bgp_session_export_path=sessionExporter, bgp_session_path=""))

    def createExporterFile(self, link, simulationADR):
        if self.nodes[link[0]]["share"]:
            proto_name = "static_bgp_" + link[0]
            bgpFile1 = "bgpSessionExporter_" + link[0] + "_" + simulationADR + ".conf"
            bgpFilePath1 = self.outPath + bgpFile1
            addressString = ""
            for i in range(self.addrToExport):
                network = self.getNetwork()
                addressString += "route " + network + "/24 via \"lo\";\n\t"

            file1 = open(bgpFilePath1, 'w')
            print addressString
            file1.write(self.bgp_session_exporter.format(session_protocol_name=proto_name,
                                                         addr_to_export=addressString))

        if self.nodes[link[1]]["share"]:
            node2Name = link[1]
            proto_name = "static_bgp_" + node2Name
            bgpFile2 = "bgpSessionExporter_" + node2Name + "_" + simulationADR + ".conf"
            bgpFilePath2 = self.outPath + bgpFile2
            addressString2 = ""
            for i in range(self.addrToExport):
                network = self.getNetwork()
                addressString2 += "route " + network + "/24 via \"lo\";"

            file2 = open(bgpFilePath2, 'w')
            file2.write(self.bgp_session_exporter.format(session_protocol_name=proto_name,
                                                         addr_to_export=addressString2))

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

    def findPrefBetweenNodes(self, n1, n2):
        for e in self.links:
            if e[0] == n1 and e[1] == n2:
                return e
        return None

    def confWithStaticRouteExporting(self, link):
        h1 = link[0]
        h2 = link[1]

        bgpString = """

        protocol bgp """ + h1 + """_""" + h2 + """ {
            local """ + str(link[2]["addr1"]).split("/")[0] + """ as """ + str(self.getAS(h1)) + """;
            neighbor """ + str(link[2]["addr2"]).split("/")[0] + """ as """ + str(self.getAS(h2)) + """;
            hold time 15;
            # debug all;
            ipv4{
                import filter bgp_in;
                export where proto = \"static_bgp_""" + h1 + """\";
            };
            connect retry time 5;
            connect delay time 10;
            startup hold time 10;
            error wait time 10,30;
            default bgp_local_pref """ + str(self.findPrefBetweenNodes(h1, h2)[2]["pref"]) + """;
            #source address """ + str(link[2]["addr1"]) + """;
        }"""
        return bgpString

    def confWithImportExportAll(self, link):
        h1 = link[0]
        h2 = link[1]

        bgpString = """

        protocol bgp """ + h1 + """_""" + h2 + """ {
            local """ + str(link[2]["addr1"]).split("/")[0] + """ as """ + str(self.getAS(h1)) + """;
            neighbor """ + str(link[2]["addr2"]).split("/")[0] + """ as """ + str(self.getAS(h2)) + """;
            hold time 15;
            # debug all;
            ipv4{
                import filter bgp_in;
                export all;
            };
            direct;
            #interface """ + h1 + """;
            connect retry time 5;
            connect delay time 10;
            startup hold time 10;
            default bgp_local_pref """ + str(self.findPrefBetweenNodes(h1, h2)[2]["pref"]) \
                    + """;
            #source address """ + str(link[2]["addr1"]) + """;
        }\n"""

        return bgpString

    def setBGPSession(self, link, strId):

        node1name = link[0]
        node2name = link[1]

        bgpFile1 = "bgpSession_" + node1name + "_" + node2name + "_" + strId + ".conf"
        bgpFile2 = "bgpSession_" + node2name + "_" + node1name + "_" + strId + ".conf"
        bgpFilePath1 = self.outPath + bgpFile1
        bgpFilePath2 = self.outPath + bgpFile2

        exportP = randint(1, 100)
        if self.nodes[link[0]]["share"]:
            bgpString1 = self.confWithImportExportAll(link)
        else:
            bgpString1 = self.confWithImportExportAll(link)

        if self.nodes[link[1]]["share"]:
            bgpString2 = self.confWithImportExportAll(link)
        else:
            bgpString2 = self.confWithImportExportAll(link)

        bgpPeer1Include = "include \"" + bgpFile1 + "\";\n"
        bgpPeer2Include = "include \"" + bgpFile2 + "\";\n"

        file1 = open(bgpFilePath1, 'w')
        file2 = open(bgpFilePath2, 'w')

        file1.write(bgpString1)
        file2.write(bgpString2)

        birdConfFile1 = self.outPath + "bird_" + link[0] + "_" + strId + ".conf"
        birdConfFile2 = self.outPath + "bird_" + link[1] + "_" + strId + ".conf"

        fileBgpConf1 = open(birdConfFile1, 'a')
        fileBgpConf2 = open(birdConfFile2, 'a')

        fileBgpConf1.write(bgpPeer1Include)
        fileBgpConf2.write(bgpPeer2Include)
