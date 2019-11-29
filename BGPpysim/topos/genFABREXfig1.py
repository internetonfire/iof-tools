#!/usr/bin/python

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
#
# Copyright (C) 2019  Mattia Milani <mattia.milani@studenti.unitn.it> & Lorenzo Ghiro <lorenzo.ghiro@unitn.it>


import networkx as nx
from collections import defaultdict


def edge(e1, e2, etype, mrai1=30.0, mrai2=30.0, customer=None):
    """
    Function to set the edge information
    :param e1: first part of the edge
    :param e2: second node of the edge
    :param etype: Type of the edge
    :param mrai1: MRAI that controls the connection e1->e2
    :param mrai2: MRAI that controls the connection e2->e1
    :param customer: Parameter that identifies which node is the customer in the relation
    :return: the edge with all the parameters configured
    """
    if etype == 'peer':
        assert customer is None
    elif etype == 'transit':
        assert customer == e1 or customer == e2
    redge = (e1, e2, {'type': etype, 'termination1': e1, 'termination2': e2,
                      'mrai1': mrai1, 'mrai2': mrai2, 'customer': customer})
    return redge


G = nx.DiGraph()

etype = 'transit'
myedges = [edge('X4', 'Y3', etype, customer='Y3', mrai1=8.0, mrai2=8.0),
           edge('X4', 'X3', etype, customer='X3', mrai1=8.0, mrai2=8.0),
           edge('Y3', 'X3', etype, customer='X3', mrai1=8.0, mrai2=8.0),
           edge('X3', 'Y2', etype, customer='Y2', mrai1=4.0, mrai2=4.0),
           edge('X3', 'X2', etype, customer='X2', mrai1=4.0, mrai2=4.0),
           edge('Y2', 'X2', etype, customer='X2', mrai1=4.0, mrai2=4.0),
           edge('X2', 'Y1', etype, customer='Y1', mrai1=2.0, mrai2=2.0),
           edge('X2', 'X1', etype, customer='X1', mrai1=2.0, mrai2=2.0),
           edge('Y1', 'X1', etype, customer='X1', mrai1=2.0, mrai2=2.0)]

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
