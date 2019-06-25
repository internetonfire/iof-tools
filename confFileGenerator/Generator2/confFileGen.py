# -*- coding: utf-8 -*-

from networkx import *
import os.path
from Node import Node
from constants import *

gname = "small_g.graphml"
outDir = "out/"

if not os.path.isfile(gname):
    small_g = internet_as_graph(50)
    nx.write_graphml(small_g, gname)

if not os.path.isdir(outDir):
    os.mkdir(outDir)

graph = read_graphml(gname)

nodes_list = list()
for n in graph.nodes(data=True):
    new_node = Node(n[0], outDir)
    if n[1][TYPE_KEY] == 'C':
        new_node.add_addr_to_export()
    nodes_list.append(new_node)
