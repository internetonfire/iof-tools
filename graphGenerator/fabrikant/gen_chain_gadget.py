#!/usr/bin/env python
from argparse import ArgumentParser
from chain_gadget import gen_chain_gadget, VALID_NODE_TYPES, VALID_EDGE_TYPES
import networkx as nx

parser = ArgumentParser()
parser.add_argument("-r", "--rings", dest="rings", required=True, type=int,
                    action="store", help="Number of rings to generate")
parser.add_argument("-i", "--inner", dest="inner", required=True, type=int,
                    action="store", help="Number of inner nodes per ring")
parser.add_argument("-o", "--outer", dest="outer", default=False,
                    action="store_true", help="Generate inner nodes as well")
parser.add_argument("-m", "--mrai", dest="mrai", default=False,
                    action="store_true", help="Generate MRAI timer attributes "
                    "as well")
parser.add_argument("-t", "--type", dest="type", default="M", action="store",
                    help="Node type. Can be either T, M, CP, or C.")
parser.add_argument("-w", "--write-to", dest="writeto",
                    default="chain_gadget.graphml", action="store",
                    help="Output graphml file where the graph will be written "
                         "to")
parser.add_argument("-l", "--weight", dest="weight", default=False,
                    action="store_true", help="Add edge weights as in the "
                                              "Fabrikant paper")
parser.add_argument("-b", "--min-mrai", dest="min_mrai", default=None,
                    action="store", type=float,
                    help="Set the minimum MRAI value that can be used. If the "
                         "minimum value computed starting from the default "
                         "(30s) larger than the minimum provided, then this "
                         "parameter is ignored. Otherwise the default value "
                         "is adapted so that the minimum timer corresponds to "
                         "the given minimum value")
args = parser.parse_args()

n_rings = args.rings
n_inner = args.inner
add_outer = args.outer
set_timer = args.mrai
node_type = args.type
edge_type = "transit"
output_file = args.writeto
min_mrai = args.min_mrai
weight = args.weight

if n_rings < 1:
    print("The number of rings must be at least 1")
    exit(1)
if n_inner < 1:
    print("The number of inner nodes must be at least 1")
    exit(1)
if node_type not in VALID_NODE_TYPES:
    print("The node type must be one of {}".format(", ".join(VALID_NODE_TYPES)))
    exit(1)
if edge_type not in VALID_EDGE_TYPES:
    print("The edge type must be one of {}".format(", ".join(VALID_EDGE_TYPES)))
    exit(1)

g = gen_chain_gadget(n_rings, n_inner, add_outer, node_type, edge_type,
                     set_timer, min_mrai, weight)
nx.write_graphml(g, output_file)
