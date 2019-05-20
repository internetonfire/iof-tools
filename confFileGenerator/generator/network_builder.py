#!/usr/bin/env python
# -*- coding: utf-8 -*-

import networkx as nx
import graph_utils as gu


class GraphNet:
    def __init__(self, edges_file, subnet):
        self.adr1 = 10
        self.adr2 = 0
        self.adr3 = 0
        self.adr4 = 1
        self.second = False

        print("Reading " + edges_file)

        g = gu.loadGraph(edges_file, connected=True)

        nodeCounter = 0
        nodeMap = {}
        max_name_len = 10 - len(str(len(g))) - 2
        for name in g.nodes(data=True):
            # remove unprintable chars from name
            nodeMap[name[0]] = "h" + filter(str.isalnum, str(name[0]))[-max_name_len:] + "_" + str(nodeCounter)
            name[1]["name"] = nodeMap[name[0]]
            nodeCounter += 1

        self.gg = nx.relabel_nodes(g, nodeMap)

        self.hosts_port = {}

        for elem in sorted(self.gg.edges(data=True)):
            # info("elem: " + str(elem) + "\n")
            if elem[2]['weight'] > 99:
                pref = 1
            elif elem[2]['weight'] < 1:
                pref = 99
            else:
                pref = 100 - elem[2]['weight']
            elem[2]["pref"] = pref

        # add nodes
        for n in sorted(self.gg.nodes(data=True)):
            n[1]["port"] = 1
            n[1]["share"] = False

        # add links infos
        for e in sorted(self.gg.edges(data=True)):
            quality_params = {}
            self.insertLink(self.gg.node[e[0]], self.gg.node[e[1]], e, subnet, quality_params)

        print self.gg.edges(data=True)

    def pickGraph(self):
        return self.gg

    def setStubNodes(self, shareFile):
        with open(shareFile, 'r') as fobj:
            all_lines = [[int(num) for num in line.split()] for line in fobj]
            for node in all_lines:
                if node[1] == 1:
                    self.gg.node["h" + str(node[0]) + "_" + str(node[0])]["share"] = True

    def pickHostAddrPort(self, node):
        port = node["port"]
        addr = "10.0." + node["name"].split('_')[-1] + "." + str(port) + "/30"
        node["port"] += 1
        return addr, port

    def pickHostAddrPortSubnet(self, node):
        port = node["port"]
        addr = str(self.adr1) + "." + str(self.adr2) + "." + str(self.adr3) + "." + str(self.adr4) + "/30"
        self.adr4 += 1
        if self.second:
            self.adr4 += 2
            self.second = False
        else:
            self.second = True
        if self.adr4 >= 255:
            self.adr3 += 1
            self.adr4 = 1
        if self.adr3 == 255:
            self.adr3 = 0
            self.adr2 += 1
        if self.adr2 == 255:
            self.adr2 = 0
            self.adr1 += 1
        if self.adr1 == 100:
            print("ERRORE Indirizzi non concessi, gli indirizzi disponibili per i link sono terminati")
        node["port"] += 1
        return addr, port

    # noinspection PyUnusedLocal
    def insertLink(self, n1, n2, link, subnet, quality_params):
        if subnet:
            addr1, port1 = self.pickHostAddrPortSubnet(n1)
            addr2, port2 = self.pickHostAddrPortSubnet(n2)
        else:
            addr1, port1 = self.pickHostAddrPort(n1)
            addr2, port2 = self.pickHostAddrPort(n2)
        print(str(subnet) + " " + str((addr1, port1)) + " " + str((addr2, port2)))
        link[2]["addr1"] = addr1
        link[2]["addr2"] = addr2
        link[2]["port1"] = port1
        link[2]["port2"] = port2
