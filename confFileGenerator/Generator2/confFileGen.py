from networkx import *
import os.path
from Node import Node

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
    new_node = Node(n[0])
    nodes_list.append(new_node)
