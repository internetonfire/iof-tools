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
# TODO not realy constants if I do this
import constants
from constants import *
import sys

# TODO i don't like this variables here
gname = ""
outDir = ""
directories = False
mrai = True
ipnetworks = ""
preferences = ""
networks = True

options, remainder = getopt.getopt(sys.argv[1:], '', ARGS)

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
    """if opt in '--nnodes':
        node_number = int(arg)"""
    if opt in '--directories':
        directories = True
    if opt in '--nomrai':
        mrai = False
    if opt in '--mraitype':
        constants.mrai_type = int(arg)
    if opt in '--prepath':
        constants.PREPATH = str(arg)
    if opt in '--ipnetworksgraph':
        ipnetworks = str(arg)
    if opt in '--noautomaticnetworks':
        networks = False
    if opt in '--preferences':
        preferences = str(arg)
    if opt in '--doublepeering':
        constants.doublepeering = True

# If the graph file is not present it will be created with a predefined number of nodes
# Creation of the file no more supported, you have to use the script made by luca:
# https://github.com/AdvancedNetworkingSystems/AS_graph_generator/tree/undirected
"""if not os.path.isfile(gname):
    small_g = internet_as_graph(node_number)
    nx.write_graphml(small_g, gname)"""

# If the output directory does not exists it will be created
if not os.path.isdir(outDir):
    os.mkdir(outDir)
else:
    shutil.rmtree(outDir)
    os.mkdir(outDir)

# I read the graph
graph = read_graphml(gname)

# I read all the nodes and I config the objects
nodes_dict = {}
for n in graph.nodes(data=True):
    # If the subdirectory system is enabled I have to create a directory for each node
    out = outDir
    if directories:
        os.mkdir(outDir + 'h_' + n[0])
        out = outDir + '/h_' + n[0] + '/'

    # TODO move this to the Node class
    # Get the networks list from the node
    ipNetworksToShare = []
    if ipnetworks in n[1]:
        ipNetworksToShare = n[1][ipnetworks].split(',')

    # Node creation
    new_node = Node(n, out)

    # If the node is of type C/CP/M it can share some addresses
    if set(n[1][TYPE_KEY]).issubset({'C', 'CP', 'M'}):
        # if there is pre-loaded addresses the node have to share them
        if len(ipNetworksToShare) >= 1:
            for net in ipNetworksToShare:
                new_node.add_addr_to_export(net)
            # Write in the main file the include to all the session exporters files
            new_node.include_in_main(new_node.sessionExporterFile_name)
        # If there is no pre-loaded networks and the networks variable is True i can load 1 address manually
        elif networks and len(ipNetworksToShare) == 0:
            new_node.add_addr_to_export()
            new_node.include_in_main(new_node.sessionExporterFile_name)
    # Add the new node to the dictionary with its name
    nodes_dict[new_node.name] = new_node

# I read all the edges and config the objects
edges_dict = {}
for edg in graph.edges(data=True):

    # TODO better solution with the attribute node_1 and node_2
    # I need to understood wich one of the two nodes is the customer to catch the node 1 and the node 2
    if {'customer'}.issubset(edg[2]):
        customer = edg[2]['customer']
        if customer != "none":
            n1 = nodes_dict[customer]
            if edg[0] == customer:
                n2 = nodes_dict[edg[1]]
            else:
                n2 = nodes_dict[edg[0]]
        else:
            n1 = nodes_dict[edg[0]]
            n2 = nodes_dict[edg[1]]
    else:
        raise Exception('customer not defined, standard not respected')

    # Set the output directory
    out1 = outDir
    out2 = outDir
    if directories:
        out1 = outDir + '/h_' + nodes_dict[edg[0]].name + '/'
        out2 = outDir + '/h_' + nodes_dict[edg[1]].name + '/',

    # Create the new edge
    new_edge = Edge(n1, n2, edg, mrai, out1, out2)

    # Insert the new edge in the dictionary
    edges_dict["h_" + str(new_edge.node1.name) + "_h_" + str(new_edge.node2.name)] = new_edge

# Write the sharing policies
for edg in edges_dict:
    edges_dict[edg].write_static_exporter()

# Write the network config script
for _, node in nodes_dict.items():
    node.write_network_configuration()

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
