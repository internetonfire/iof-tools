#!/usr/bin/env python

# This script selects an arbitrary number of random nodes from a
# topology graph. It has been used to select the nodes originating
# a change in the network in the "Elmokashfi" simulations.

from networkx import *
from argparse import ArgumentParser
from random import randint

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-g", "--graph", dest="graph",required=True,
                        default="", action="store",
                        help="Graphml file")
    parser.add_argument("-t", "--type", dest="type", default="", action="store",
                        help = "Node type. Can be either T, M, CP, or C.")
    parser.add_argument("-n", "--num", dest="num", default=5, action="store",
                        help="Number of AS to extract")
    parser.add_argument("-l", "--leaf", dest="leaf", required=False, action = "store_true",
                        help = "Forces the selected node to be a leaf")


    args = parser.parse_args()

    graph = read_graphml(args.graph)

    num = int(args.num)

    if args.leaf and args.type != "C":
        print("Only C nodes can be leafs.")
        exit()
    if num < 1:
        print("Number of AS to extract too low")
        exit()

    nodes_num = graph.number_of_nodes()
    nodes_list = list(graph.nodes(data=True))

    extracted_nodes = 0
    while extracted_nodes < num:
        r = randint(0,nodes_num-1)

        if args.type == "":
            print("ID: {}".format(r))
            extracted_nodes += 1
        else:
            t = nodes_list[r][1]['type']
            #print(t)
            if t != args.type:
                continue
            if args.leaf:
                # Need to be a leaf
                deg = graph.degree[nodes_list[r][0]]
                #print(deg)
                if deg != 1:
                    continue
                else:
                    print("ID: {}".format(r))
                    extracted_nodes += 1
            else:
                print("ID: {}".format(r))
                extracted_nodes += 1

