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

# This script adds destinations to a graphml file.
# The destinations are taken from the 100.0.0.0/8 netblock. 
# The destinations will be added to all the nodes, excluded the
# Tier-1 nodes.
#
from networkx import *
from argparse import ArgumentParser
import ipaddress


if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-g", "--graph", dest="graph",required=True,
                        default="", action="store",
                        help="Graphml file")
    parser.add_argument("-o","--out", dest="outgraph",required=True,
                        default="output.graphml", action="store",
                        help="Graphml output filename")

    args = parser.parse_args()

    graph = read_graphml(args.graph)

    node_networks = list(ipaddress.ip_network(u'100.0.0.0/8').subnets(new_prefix=24))

    i = 0
    for n in graph.nodes(data=True):
        if n[1]['type'] == 'C' or n[1]['type'] == 'CP' or n[1]['type'] == 'M':
            n[1]['destinations'] = str(node_networks[i])
        i += 1

    #for n in graph.nodes(data=True):
    #    print(n[1]['destinations'])

    nx.write_graphml(graph, args.outgraph)
