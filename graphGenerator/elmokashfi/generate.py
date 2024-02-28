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
import sys
from argparse import ArgumentParser
import bgp
import networkx as nx

def usage(name):
    print("Usage:")
    print(f"\t{name} <number_of_nodes> <number_of_graphs>")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-n", "--nodes", dest="nodes",
                        type=int, default=0, action="store",
                        help="Number of nodes of the Graph")
    parser.add_argument("-g", "--graphs", dest="graphs",
                        type=int, default=1, action="store",
                        help="Number of Graphs to generate, default 1")
    parser.add_argument("-s", "--seed", dest="seed",
                        type=int, default=None, action="store",
                        help="Seed number to initialize the RNG")

    args = parser.parse_args()
    nodes = args.nodes
    graphs = args.graphs
    if args.nodes <= 0:
        print("You must specify a valid number of nodes")
        exit(1)

    if args.seed and graphs > 1:
        print("You cannot specify a seed and a number of graphs higher than 1")
        exit(1)

    for i in range(graphs):
        if args.seed:
            G = bgp.internet_as_graph(nodes,args.seed)
        else:
            G = bgp.internet_as_graph(nodes)
        nx.write_graphml(G, f"baseline-{nodes}-{i}.graphml")
