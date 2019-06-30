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


options, remainder = getopt.getopt(sys.argv[1:], '', ['graph=',
                                                      'out='
                                                      ])
# print 'OPTIONS   :', [x[0] for x in options]
if {'--graph', '--out'} != set([x[0] for x in options]):
    print("Mandatory args are: ", '--graph (Graph file)', '--out (Output folder)')
    sys.exit(1)
for opt, arg in options:
    if opt in '--graph':
        gname = arg
    if opt in '--out':
        outDir = arg

# If the graph file is not present it will be created with a predefined number of nodes
if not os.path.isfile(gname):
    small_g = internet_as_graph(node_number)
    nx.write_graphml(small_g, gname)

# If the output dire does not exists it will be created
if not os.path.isdir(outDir):
    os.mkdir(outDir)

# I read the graph
graph = read_graphml(gname)

# I read all the nodes and I config the objects
nodes_dict = {}
for n in graph.nodes(data=True):
    new_node = Node(n[0], n[1]['type'], outDir)
    # If the node is of type c it will share some addresses
    if n[1][TYPE_KEY] == 'C':
        new_node.add_addr_to_export()
    nodes_dict[n[0]] = new_node

# I read all the edges and config the objects
edges_dict = {}
for edg in graph.edges(data=True):
    new_edge = Edge(nodes_dict[edg[0]], nodes_dict[edg[1]], edg[2]['type'], outDir)
    edges_dict["h_" + str(new_edge.node1.name) + "_h_" + str(new_edge.node2.name)] = new_edge

# Write the sharing policies
for edg in edges_dict:
    edges_dict[edg].write_static_exporter()

# Copy the base files to the simulation directory
src_files = os.listdir(src)
for file_name in src_files:
    full_file_name = os.path.join(src, file_name)
    if os.path.isfile(full_file_name):
        shutil.copy(full_file_name, outDir)