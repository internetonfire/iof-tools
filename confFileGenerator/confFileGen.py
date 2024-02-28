#!/usr/bin/env python
#==============================================================================
# Copyright (C) 2019-2024 Mattia Milani, Leonardo Maccari, Luca Baldesi, Lorenzo Ghiro, Michele Segata, Marco Nesler 
#
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
#==============================================================================
# -*- coding: utf-8 -*-

import getopt
import os.path
import shutil
import sys

from Edge import Edge
from Node import Node
from notConstants import NotConstantsObj
from constants import *
from networkx import *

variables = NotConstantsObj()

options, remainder = getopt.getopt(sys.argv[1:], '', ARGS)

if set([x[0] for x in options]).issubset({'--help', '-h'}):
    print(HELP_MESSAGE)
    sys.exit(0)
if not {'--graph', '--out'}.issubset(set([x[0] for x in options])):
    print(HELP_MESSAGE)
    sys.exit(1)
for opt, arg in options:
    if opt in '--graph':
        variables.gname = arg
    if opt in '--out':
        variables.outDir = arg
    if opt in '--directories':
        variables.directories = True
    if opt in '--nomrai':
        variables.mrai = False
    if opt in '--mraitype':
        variables.mrai_type = int(arg)
    if opt in '--mraijitter':
        variables.mrai_jitter = int(arg)
    if opt in '--prepath':
        variables.PREPATH = str(arg)
    if opt in '--ipnetworksgraph':
        variables.ipNetworks = str(arg)
    if opt in '--noautomaticnetworks':
        variables.networks = False
    if opt in '--doublepeering':
        variables.doublePeering = True
    if opt in '--fatallog':
        variables.log_mode = "{fatal}"
    if opt in '--prefevaluator':
        variables.pref_eval = str(arg)

# If the graph file is not present it will be created with a predefined number of nodes
# Creation of the file no more supported, you have to use the script made by Luca:
# https://github.com/AdvancedNetworkingSystems/AS_graph_generator/tree/undirected
"""if not os.path.isfile(variables.gname):
    small_g = internet_as_graph(node_number)
    nx.write_graphml(small_g, variables.gname)"""

# If the output directory does not exists it will be created
if not os.path.isdir(variables.outDir):
    os.mkdir(variables.outDir)
else:
    shutil.rmtree(variables.outDir)
    os.mkdir(variables.outDir)

# I read the graph
graph = read_graphml(variables.gname)

# I read all the nodes and I config the objects
nodes_dict = {}
for n in graph.nodes(data=True):
    # If the subdirectory system is enabled I have to create a directory for each node
    out = variables.outDir
    if variables.directories:
        os.mkdir(variables.outDir + 'h_' + n[0])
        out = variables.outDir + '/h_' + n[0] + '/'

    # Node creation
    new_node = Node(n, out, variables)

    new_node.install_networks()
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
            n1 = nodes_dict[str(customer)]
            if edg[0] == str(customer):
                n2 = nodes_dict[edg[1]]
            else:
                n2 = nodes_dict[edg[0]]
        else:
            n1 = nodes_dict[edg[0]]
            n2 = nodes_dict[edg[1]]
    else:
        raise Exception('customer not defined, standard not respected')

    # Set the output directory
    out1 = variables.outDir
    out2 = variables.outDir
    if variables.directories:
        out1 = variables.outDir + '/h_' + n1.name + '/'
        out2 = variables.outDir + '/h_' + n2.name + '/'
        out1.replace("//", "/")
        out2.replace("//", "/")

    # Create the new edge
    new_edge = Edge(n1, n2, edg, out1, out2, variables)

    # Insert the new edge in the dictionary
    edges_dict["h_" + str(new_edge.node1.name) + "_h_" + str(new_edge.node2.name)] = new_edge

# Write the sharing policies
for edg in edges_dict:
    edges_dict[edg].write_static_exporter()

# Write the network config script
for _, node in nodes_dict.items():
    node.write_network_configuration()

with open(PREF_COMMON_FILTER, "r") as filter_file:
    filter_template = filter_file.read()
commonFiltersFile = open("baseFiles/commonFilters.conf", 'w')
if variables.pref_eval != "":
    with open(variables.pref_eval, "r") as prefFile:
        prefFunctionName = prefFile.readline().split(' ')[-1].split('(')[0]
    shutil.copy(variables.pref_eval, "baseFiles/prefFile.conf")
    variables.pref_eval = "prefFile.conf"
    commonFiltersFile.write(
        filter_template.format(IMPORT_BGP_PREF="include \"" + variables.pref_eval + "\";",
                               BGP_PREF_FUNCTION=prefFunctionName + "();"))
else:
    commonFiltersFile.write(
        filter_template.format(IMPORT_BGP_PREF="", BGP_PREF_FUNCTION=""))
commonFiltersFile.close()

# Copy the base files to the simulation directory
if not variables.directories:
    src_files = os.listdir(src)
    for file_name in src_files:
        full_file_name = os.path.join(src, file_name)
        if os.path.isfile(full_file_name):
            shutil.copy(full_file_name, variables.outDir)
else:
    src_files = os.listdir(src)
    for file_name in src_files:
        full_file_name = os.path.join(src, file_name)
        if os.path.isfile(full_file_name):
            for node in graph.nodes(data=True):
                out = variables.outDir + 'h_' + node[0]
                shutil.copy(full_file_name, out)
