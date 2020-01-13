#!/usr/bin/env python

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
