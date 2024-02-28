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
from argparse import ArgumentParser
import networkx as nx
from graphGenerator.chain_gadget import VALID_NODE_TYPES, VALID_EDGE_TYPES, ATTR_NODE_TYPE, \
    ATTR_EDGE_TYPE

parser = ArgumentParser()
parser.add_argument("-n", "--nodes", dest="nodes", required=True, type=int,
                    action="store", help="Total number of ASes")
parser.add_argument("-t", "--type", dest="type", default="T", action="store",
                    help="Node type. Can be either T, M, CP, or C.")
parser.add_argument("-w", "--write-to", dest="writeto",
                    default="complete_graph.graphml", action="store",
                    help="Output graphml file where the graph will be written "
                         "to")
args = parser.parse_args()

nodes = args.nodes
node_type = args.type
edge_type = "peer"
output_file = args.writeto

if nodes < 2:
    print("The number of nodes (ASes) must be at least 2")
    exit(1)
if node_type not in VALID_NODE_TYPES:
    print("The node type must be one of {}".format(", ".join(VALID_NODE_TYPES)))
    exit(1)
if edge_type not in VALID_EDGE_TYPES:
    print("The edge type must be one of {}".format(", ".join(VALID_EDGE_TYPES)))
    exit(1)

g = nx.complete_graph(nodes, create_using=nx.DiGraph())
nx.set_node_attributes(g, node_type, ATTR_NODE_TYPE)
nx.set_edge_attributes(g, edge_type, ATTR_EDGE_TYPE)
nx.write_graphml(g, output_file)
