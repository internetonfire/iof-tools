#!/usr/bin/env python
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
