# -*- coding: utf-8 -*-

from networkx import *
import os.path
import shutil
from Node import Node
from Edge import Edge
from constants import *

gname = "small_g.graphml"
outDir = "out/"
src = "../baseFiles/"

if not os.path.isfile(gname):
    small_g = internet_as_graph(50)
    nx.write_graphml(small_g, gname)

if not os.path.isdir(outDir):
    os.mkdir(outDir)

graph = read_graphml(gname)

nodes_dict = {}
for n in graph.nodes(data=True):
    new_node = Node(n[0], n[1]['type'], outDir)
    if n[1][TYPE_KEY] == 'C':
        new_node.add_addr_to_export()
    nodes_dict[n[0]] = new_node

edges_dict = {}
for edg in graph.edges(data=True):
    new_edge = Edge(nodes_dict[edg[0]], nodes_dict[edg[1]], edg[2]['type'], outDir)
    edges_dict["h_" + str(new_edge.node1.name) + "_h_" + str(new_edge.node2.name)] = new_edge

for edg in edges_dict:
    edges_dict[edg].write_static_exporter()

# Copy the base files to the simulation directory
src_files = os.listdir(src)
for file_name in src_files:
    full_file_name = os.path.join(src, file_name)
    if os.path.isfile(full_file_name):
        shutil.copy(full_file_name, outDir)