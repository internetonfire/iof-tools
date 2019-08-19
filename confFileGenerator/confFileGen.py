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

import getopt
from networkx import *
import os.path
import shutil
from Node import Node
from Edge import Edge
from constants import *
import sys

gname = ""
outDir = ""
directories = False

options, remainder = getopt.getopt(sys.argv[1:], '', ['graph=',
                                                      'out=',
                                                      'nnodes=',
                                                      'directories',
                                                      'help',
                                                      'h'
                                                      ])
if set([x[0] for x in options]).issubset({'--help', '-h'}):
    print(HELP_MESSAGE)
    sys.exit(0)
if not {'--graph', '--out'}.issubset(set([x[0] for x in options])):
    print(HELP_MESSAGE)
    sys.exit(1)
for opt, arg in options:
    if opt in '--graph':
        gname = arg
    if opt in '--out':
        outDir = arg
    if opt in '--nnodes':
        node_number = int(arg)
    if opt in '--directories':
        directories = True

# If the graph file is not present it will be created with a predefined number of nodes
if not os.path.isfile(gname):
    small_g = internet_as_graph(node_number)
    nx.write_graphml(small_g, gname)

# If the output dire does not exists it will be created
if not os.path.isdir(outDir):
    os.mkdir(outDir)
else:
    shutil.rmtree(outDir)
    os.mkdir(outDir)

# I read the graph
graph = read_graphml(gname)

if directories:
    for node in graph.nodes(data=True):
        os.mkdir(outDir + 'h_' + node[0])

# I read all the nodes and I config the objects
nodes_dict = {}
for n in graph.nodes(data=True):
    if 'mrai' in n[1]:
        if directories:
            new_node = Node(n[0], n[1]['type'], outDir + '/h_' + n[0] + '/', n[1]['mrai'])
        else:
            new_node = Node(n[0], n[1]['type'], outDir, n[1]['mrai'])
    else:
        if directories:
            new_node = Node(n[0], n[1]['type'], outDir + '/h_' + n[0] + '/')
        else:
            new_node = Node(n[0], n[1]['type'], outDir)
    # If the node is of type c it will share some addresses
    if n[1][TYPE_KEY] == 'C':
        new_node.add_addr_to_export()
    nodes_dict[n[0]] = new_node

# I read all the edges and config the objects
edges_dict = {}
for edg in graph.edges(data=True):
    ipAddrEth1 = ""
    ipAddrEth2 = ""

    if {'ip_eth_n1', 'ip_eth_n2'}.issubset(edg[2]):
        ipAddrEth1 = edg[2]['ip_eth_n1']
        ipAddrEth2 = edg[2]['ip_eth_n2']

    if directories:
        new_edge = Edge(nodes_dict[edg[0]], nodes_dict[edg[1]], edg[2]['type'], [ipAddrEth1, ipAddrEth2],
                        outDir + '/h_' + nodes_dict[edg[0]].name + '/', outDir + '/h_' + nodes_dict[edg[1]].name + '/')
    else:
        new_edge = Edge(nodes_dict[edg[0]], nodes_dict[edg[1]], edg[2]['type'], [ipAddrEth1, ipAddrEth2],
                        outDir, outDir)
    edges_dict["h_" + str(new_edge.node1.name) + "_h_" + str(new_edge.node2.name)] = new_edge

# Write the sharing policies
for edg in edges_dict:
    edges_dict[edg].write_static_exporter()

# Copy the base files to the simulation directory
if not directories:
    src_files = os.listdir(src)
    for file_name in src_files:
        full_file_name = os.path.join(src, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, outDir)
else:
    src_files = os.listdir(src)
    for file_name in src_files:
        full_file_name = os.path.join(src, file_name)
        if os.path.isfile(full_file_name):
            for node in graph.nodes(data=True):
                out = outDir + 'h_' + node[0]
                shutil.copy(full_file_name, out)
