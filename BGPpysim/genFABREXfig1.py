#!/usr/bin/python

import code
import networkx as nx
from collections import defaultdict


def edge(e1, e2, etype, mrai1=30, mrai2=30, customer=None):
    if etype == 'peer':
        assert customer == None
    elif etype == 'transit':
        assert customer == e1 or customer == e2
    redge = (e1, e2, {'type': etype, 'termination1': e1, 'termination2': e2,
                      'mrai1': mrai1, 'mrai2': mrai2, 'customer': customer})
    return redge


G = nx.DiGraph()

etype = 'transit'
myedges = []
myedges.append(edge('X4', 'Y3', etype, customer='X4', mrai1=7.5, mrai2=7.5))
myedges.append(edge('X4', 'X3', etype, customer='X4', mrai1=7.5, mrai2=7.5))
myedges.append(edge('Y3', 'X3', etype, customer='Y3', mrai1=7.5, mrai2=7.5))

myedges.append(edge('X3', 'Y2', etype, customer='X3', mrai1=15.0, mrai2=15.0))
myedges.append(edge('X3', 'X2', etype, customer='X3', mrai1=15.0, mrai2=15.0))
myedges.append(edge('Y2', 'X2', etype, customer='Y2', mrai1=15.0, mrai2=15.0))

myedges.append(edge('X2', 'Y1', etype, customer='X2', mrai1=30.0, mrai2=30.0))
myedges.append(edge('X2', 'X1', etype, customer='X2', mrai1=30.0, mrai2=30.0))
myedges.append(edge('Y1', 'X1', etype, customer='Y1', mrai1=30.0, mrai2=30.0))


G.add_edges_from(myedges)

attrs = defaultdict(dict)
# Source export dest d
ntype = 'C'
for n in G.nodes():
    destinations = []
    if n == 'X1':
        destinations = ['100.0.0.0/24']
    attrs[n]['destinations'] = ','.join(destinations)
    attrs[n]['type'] = ntype

nx.set_node_attributes(G, attrs)

nx.write_graphml(G, 'test.graphml')
#code.interact(local=dict(globals(), **locals()))
