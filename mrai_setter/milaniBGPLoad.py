#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
# Copyright (C) 2019  Mattia Milani <mattia.milani@studenti.unitn.it>
"""Milani Centrality."""
from operator import itemgetter

import networkx as nx



def mice_centrality(G, cutoff=None, normalized=True, weight=None, destIdentifier='destinations'):
    """Compute distributed partial centrality for nodes.

    The centrality of a node is the fraction of all shortest
    paths that pass through that node.

    Parameters
    ----------
    G : graph
      A networkx graph.

    normalized : bool, optional (default=True)
      If True the dpc values are normalized by b=b/(n-1)(n-2) where
      n is the number of nodes in the destination set.

    weight : None or string, optional (default=None)
      If None, edge weights are ignored.
      Otherwise holds the name of the edge attribute used as weight.

    destIdentifier : string, (identifier for the stub nodes)
      If specified is a parameter used to discern between stub nodes and transit nodes

    Returns
    -------
    nodes : dictionary
       Dictionary of nodes with centrality as the value.

    See Also
    --------
    betweenness_centrality()
    """

    # Initlally all loads are 0
    dpc_load = {}.fromkeys(G, 0.0)
    dpc = {}
    # Take the list of stub nodes
    nodeList = [i for i in G.nodes if destIdentifier in G.nodes[i]]
    for node in nodeList:
        dpc[node] = 0.0  # For each initial stub node I set a dpc of 0

    # Calculate the load dispersione between each couple of stub nodes
    for source in dpc:
        ubetween = _node_betweenness(G, source, cutoff, weight, destIdentifier=destIdentifier)
        for vk in ubetween:
            dpc_load[vk] += ubetween[vk]

    if normalized:
        order = len(nodeList)
        if order <= 1:
            return dpc_load  # no normalization for only 1 node
        scale = 1/(order * (order - 1))  # scale is 1/ two times the summarized input load
        for v in dpc_load:
            dpc_load[v] *= scale  # For each element in the load the final load is the actual load multiplied by scale
    return dpc_load  # all nodes


def _node_betweenness(G, source, cutoff=False, weight=None, destIdentifier='destinations'):
    """Node betweenness_centrality helper:

    See betweenness_centrality for what you probably want.
    This actually computes "partial centrality" and not betweenness.
    See https://networkx.lanl.gov/ticket/103

    This calculates the load of each node for paths from a single source.
    (The fraction of number of shortests paths from source that go
    through each node.)

    To get the load for a node you need to do all-pairs shortest paths.

    If weight is not None then use Dijkstra for finding shortest paths.
    """
    # get the predecessor and path length data
    if weight is None:
        (pred, length) = nx.predecessor(G, source, cutoff=cutoff,
                                        return_seen=True)
    else:
        (pred, length) = nx.dijkstra_predecessor_and_distance(G, source,
                                                              cutoff, weight)

    for predecessor in pred:
        newlist = []
        if len(pred[predecessor]) > 0:
            minimo = pred[predecessor][0]
            for elem in pred[predecessor]:
                if int(elem) < int(minimo):
                    minimo = elem
            newlist.append(minimo)
            pred[predecessor][:] = newlist

    onodes = [(l, vert) for (vert, l) in length.items()]
    onodes.sort()
    onodes[:] = [vert for (l, vert) in onodes if l > 0]

    between = {}.fromkeys(length, 1.0)
    for node in G.nodes:
        if destIdentifier not in G.nodes[node]:
            between[node] = 0.0  # No stub nodes does not propagate any contribute
        else:
            between[node] = 1.0  # Stub nodes propagate 1 contribute

    while onodes:
        v = onodes.pop()
        if v in pred:
            num_paths = len(pred[v])  # Discount betweenness if more than
            for x in pred[v]:  # one shortest path.
                if x == source:  # stop if hit source
                    break  # also have pred[v]==[source]
                between[x] += between[v] / float(num_paths)

    for node in G.nodes:
        if destIdentifier in G.nodes[node]:
            between[node] -= 1.0

    return between
