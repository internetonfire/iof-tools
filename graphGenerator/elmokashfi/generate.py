#!/usr/bin/env python
import sys


def usage(name):
    print("Usage:")
    print(f"\t{name} <number_of_nodes> <number_of_graphs>")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        usage(sys.argv[0])
    else:
        import bgp
        import networkx as nx
        nodes = int(sys.argv[1])
        graphs = int(sys.argv[2])
        for i in range(graphs):
            G = bgp.internet_as_graph(nodes)
            nx.write_graphml(G, f"baseline-{nodes}-{i}.graphml")
