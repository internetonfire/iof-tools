# -*- coding: utf-8 -*-

from networkx import *
import os.path
from Node import Node
from Edge import Edge
from constants import *

gname = "small_g.graphml"
outDir = "out/"

if not os.path.isfile(gname):
    small_g = internet_as_graph(50)
    nx.write_graphml(small_g, gname)

if not os.path.isdir(outDir):
    os.mkdir(outDir)

graph = read_graphml(gname)

nodes_dict = {}
for n in graph.nodes(data=True):
    new_node = Node(n[0], outDir)
    if n[1][TYPE_KEY] == 'C':
        new_node.add_addr_to_export()
    nodes_dict[n[0]] = new_node

for edg in graph.edges(data=True):
    new_edge = Edge(nodes_dict[edg[0]], nodes_dict[edg[1]], outDir)
    print(str(new_edge))
