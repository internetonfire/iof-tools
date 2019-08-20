#!/usr/bin/python

import code
import networkx as nx
from collections import defaultdict

G = nx.DiGraph()

# 1-hop metric/weight
myedges = []
myedges += ('X4', 'Y3', {'weight': 1, 'type': 'transit'}),
myedges += ('X4', 'X3', {'weight': 1, 'type': 'transit'}),
myedges += ('X3', 'Y2', {'weight': 1, 'type': 'transit'}),
myedges += ('X3', 'X2', {'weight': 1, 'type': 'transit'}),
myedges += ('X2', 'Y1', {'weight': 1, 'type': 'transit'}),
myedges += ('X2', 'X1', {'weight': 1, 'type': 'transit'}),

# they were originally unlabeled
myedges += ('Y3', 'X3', {'weight': 1, 'type': 'transit'}),
myedges += ('Y2', 'X2', {'weight': 1, 'type': 'transit'}),
myedges += ('Y1', 'X1', {'weight': 1, 'type': 'transit'}),

# one link only from X1 to source, at run-time we will have
# to increase the weight to trigger the exponential path-exploration
myedges += ('X1', 'SOURCE', {'weight': 1, 'type': 'transit'}),

G.add_edges_from(myedges)

attrs = defaultdict(dict)
# Source export dest d
attrs['SOURCE']['ipNetworksToShare'] = 'd'
# Setting MRAI for all nodes
attrs['SOURCE']['mrai'] = 16
attrs['X1']['mrai'] = 8
attrs['Y1']['mrai'] = 8
attrs['X2']['mrai'] = 4
attrs['Y2']['mrai'] = 4
attrs['X3']['mrai'] = 2
attrs['Y3']['mrai'] = 2
attrs['X4']['mrai'] = 1

# Type of nodes
attrs['SOURCE']['type'] = 'C'
attrs['X1']['type'] = 'M'
attrs['Y1']['type'] = 'M'
attrs['X2']['type'] = 'M'
attrs['Y2']['type'] = 'M'
attrs['X3']['type'] = 'M'
attrs['Y3']['type'] = 'M'
attrs['X4']['type'] = 'M'


nx.set_node_attributes(G, attrs)

# G.nodes['SOURCE'].addAttribute("PrefixList"=['d'])

nx.write_graphml(G, 'test.graphml')
code.interact(local=dict(globals(), **locals()))
