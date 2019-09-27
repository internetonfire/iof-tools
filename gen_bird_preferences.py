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
from argparse import ArgumentParser
import networkx as nx

parser = ArgumentParser()
parser.add_argument("-w", "--write-to", dest="writeto",
                    default="pref.conf", action="store",
                    help="Output conf file where the configuration will be written")
parser.add_argument("-g", "--graph", dest="graph", required=True, type=str, action="store")

args = parser.parse_args()

mlgraph = args.graph
out = args.writeto

graph = nx.read_graphml(mlgraph)

for node in graph.nodes(data=True):
    if "destinations" in node[1].keys():
        destinationNode = node
        break

maxMrai = 30.0

for edge in graph.edges(data=True):
    if edge[2]["mrai1"] > maxMrai:
        maxMrai = edge[2]["mrai1"]
    elif edge[2]["mrai2"] > maxMrai:
        maxMrai = edge[2]["mrai2"]

n1 = str(int(destinationNode[0]) + 1)
n2 = str(int(destinationNode[0]) + 2)
n3 = str(int(destinationNode[0]) + 3)

graph.add_node(n1, type="M")
graph.add_node(n2, type="M")
graph.add_node(n3, type="M", destinations=destinationNode[1]["destinations"])

graph.add_edge(n1, destinationNode[0], customer=n1, termination1=n1, termination2=destinationNode[0],
               mrai1=maxMrai, mrai2=maxMrai, fabrikant_weight=0, type="transit")
graph.add_edge(n2, destinationNode[0], customer=n2, termination1=n2, termination2=destinationNode[0],
               mrai1=maxMrai, mrai2=maxMrai, fabrikant_weight=1, type="transit")
graph.add_edge(n3, n1, customer=n3, termination1=n3, termination2=n1,
               mrai1=maxMrai, mrai2=maxMrai, type="transit")
graph.add_edge(n3, n2, customer=n3, termination1=n3, termination2=n2,
               mrai1=maxMrai, mrai2=maxMrai, type="transit")

del graph.node[destinationNode[0]]["destinations"]

destinationNode = (str(n3), graph.node[n3])

G = nx.DiGraph()
for node in graph.nodes(data=True):
    G.add_node(str(node[0]))

for edge in graph.edges(data=True):
    e1 = str(edge[2]["customer"])
    if e1 == str(edge[2]["termination1"]):
        e2 = str(edge[2]["termination2"])
    else:
        e2 = str(edge[2]["termination1"])
    G.add_edge(e1, e2)

pathSet = set()

for node in G.nodes():
    # print("All paths from " + str(node[0]) + " to " + str(destinationNode[0]))
    for path in nx.all_simple_paths(G, destinationNode[0], node[0]):
        pathSet.add(tuple(path))

pathlist = sorted(list(pathSet), key=len)

pathPref = {}
for path in pathlist:
    i = 0
    j = 1
    pathPref[str(path)] = ""
    while j < len(path):
        e = (path[i], path[j])
        edge = graph.get_edge_data(*e)
        if edge == None:
            e = (path[j], path[i])
            edge = graph.get_edge_data(*e)

        if "fabrikant_weight" in edge:
            pathPref[str(path)] += str(edge["fabrikant_weight"])
        i += 1
        j += 1

for key in pathPref:
    if pathPref[key] != '':
        pathPref[key] = 100 + int(pathPref[key].zfill(32), 2)
    else:
        pathPref[key] = 10

singlePrefFile = "templates/singlePref.template"
prefFile = "templates/prefFile.template"

with open(singlePrefFile, "r") as singlePref:
    singlePref_template = singlePref.read()
with open(prefFile, "r") as pref:
    pref_template = pref.read()

singlePref_list = []
for key in pathPref:
    path = key.replace('(', '').replace(')', '').replace(',', ' ').replace('\'', '')
    pref = pathPref[key]
    singlePref_list.append(singlePref_template.format(PATH=path, PREFERENCE=pref))

with open(out, "w") as outFile:
    outFile.write(
        pref_template.format(PREFERENCES_LIST=''.join(singlePref_list), DEFAULT_PREF="1")
    )
nx.write_graphml(graph, mlgraph.split('.')[0] + "_2.graphml")
