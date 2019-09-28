#!/usr/bin/env python3
# Author: Luca Baldesi 2019

import sys
import networkx as nx
import functools

import milaniBGPLoad as mice


strategies = []


def usage(name):
    print("Usage:")
    print(f"\t{name} <graphml_file> <strategy> [<advertising_node>]")
    print("\nAvailable strategies:")
    pp = "\t" 
    pp += ", ".join(strategies)
    print(pp)


def bgp_strategy(func):
    ''' Wrapper for strategy definition; it adds strategy name to the strategy list.
    Strategy name *must not* include an underscore and the function *must* be 
    called "apply_<strategyname>_strategy".
    '''
    strategies.append(func.__qualname__.split('_')[1])
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper


@bgp_strategy
def apply_30secs_strategy(G, adv_node):
    ''' set all mrai timers to 30 '''
    for e in G.edges:
        i, j = e
        G.edges[e]['termination1'] = i 
        G.edges[e]['termination2'] = j 
        G.edges[e]['mrai1'] = 30.0
        G.edges[e]['mrai2'] = 30.0


@bgp_strategy
def apply_none_strategy(G, adv_node):
    ''' set all mrai timers to 0 '''
    for e in G.edges:
        i, j = e
        G.edges[e]['termination1'] = i 
        G.edges[e]['termination2'] = j 
        G.edges[e]['mrai1'] = 0.0
        G.edges[e]['mrai2'] = 0.0


@bgp_strategy
def apply_fabrikant_strategy(G, adv_node):
    ''' set mrai timers according to the Fabrikant gadget paper '''
    fl = fabrikant_levels(G, adv_node)
    for i in G.nodes:
        if i in fl:
            set_node_mrai(G, i, 30/(2**fl[i]))
        else:
            set_node_mrai(G, i, 30)


@bgp_strategy
def apply_inversefabrikant_strategy(G, adv_node):
    ''' set mrai timers according to the Fabrikant gadget paper
    but in reverse order '''
    fl = fabrikant_levels(G, adv_node)
    maxi = max(fl.values())
    for i in G.nodes:
        if i in fl:
            set_node_mrai(G, i, 30/(2**(maxi-fl[i])))
        else:
            set_node_mrai(G, i, 30)


@bgp_strategy
def apply_simpleheuristic_strategy(G, adv_node):
    ''' set mrai timers so that they slightly increase as updates get
    farther and farther from the advertising node '''
    start_mrai = 0
    inc_mrai = 0.5
    mrai = {}

    visited_nodes = set()
    mrai[adv_node] = start_mrai
    set_node_mrai(G, adv_node, mrai[adv_node])
    fifo = set()
    for j in nx.neighbors(G, adv_node):
        fifo.add((adv_node, j))

    while len(fifo) > 0:
        i, j = fifo.pop()
        if j not in visited_nodes:
            mrai[j] = mrai[i] + inc_mrai
            set_node_mrai(G, j, mrai[j])
            visited_nodes.add(j)

            e = G.edges[(i,j)]
            if str(e['customer']) == i:
                for z in nx.neighbors(G, j):
                    if z != i and z not in visited_nodes:
                        fifo.add((j, z))
            else:
                for z in nx.neighbors(G, j):
                    if str(G.edges[(j, z)]['customer']) == z and z not in visited_nodes:
                        fifo.add((j, z))


@bgp_strategy
def apply_milanicent_strategy(G, adv_node):
    ''' set mrai timers so accordingly to Milani centrality (MiCe).
    Graph is split in three logic parts. '''
    T = 30.0  # max mrai in seconds
    cent = mice.mice_centrality(G, normalized=True)

    visited_nodes = set()
    set_node_mrai(G, adv_node, T*cent[adv_node]/2)
    fifo = set()
    for j in nx.neighbors(G, adv_node):
        fifo.add((adv_node, j))

    while len(fifo) > 0:
        i, j = fifo.pop()
        if j not in visited_nodes:
            e = G.edges[(i,j)]
            if str(e['customer']) == j:  # we are in phase 3
                set_node_mrai(G, j, T*cent[j]/2)
            elif G.nodes[j]['type'] == 'T':  # we are in phase 2
                set_node_mrai(G, j, T/2)
            else:  # we are in phase 3
                set_node_mrai(G, j, T*(2-cent[j])/2)
            visited_nodes.add(j)

            if str(e['customer']) == i:
                for z in nx.neighbors(G, j):
                    if z != i and z not in visited_nodes:
                        fifo.add((j, z))
            else:
                for z in nx.neighbors(G, j):
                    if str(G.edges[(j, z)]['customer']) == z and z not in visited_nodes:
                        fifo.add((j, z))


@bgp_strategy
def apply_milanicent2_strategy(G, adv_node):
    ''' set mrai timers so accordingly to Milani centrality (MiCe).
    Graph is split in three logic parts. '''
    T = 30.0  # max mrai in seconds
    cent = mice.mice_centrality(G, normalized=False)
    ss = max(cent.values())
    cent = {i: v/ss for i,v in cent.items()}

    visited_nodes = set()
    set_node_mrai(G, adv_node, T*cent[adv_node]/2)
    fifo = set()
    for j in nx.neighbors(G, adv_node):
        fifo.add((adv_node, j))

    while len(fifo) > 0:
        i, j = fifo.pop()
        if j not in visited_nodes:
            e = G.edges[(i,j)]
            if str(e['customer']) == j:  # we are in phase 3
                set_node_mrai(G, j, T*cent[j]/2)
            elif G.nodes[j]['type'] == 'T':  # we are in phase 2
                set_node_mrai(G, j, T/2)
            else:  # we are in phase 3
                set_node_mrai(G, j, T*(2-cent[j])/2)
            visited_nodes.add(j)

            if str(e['customer']) == i:
                for z in nx.neighbors(G, j):
                    if z != i and z not in visited_nodes:
                        fifo.add((j, z))
            else:
                for z in nx.neighbors(G, j):
                    if str(G.edges[(j, z)]['customer']) == z and z not in visited_nodes:
                        fifo.add((j, z))


def set_node_mrai(G, node, mrai):
    for j in nx.neighbors(G, node):
        e = G.edges[(node, j)]
        if 'termination1' in e:
            if e['termination1'] == node:
                e['mrai1'] = float(mrai)
            else:
                e['mrai2'] = float(mrai)
        else:
            e['termination1'] = node
            e['mrai1'] = float(mrai)
            e['termination2'] = j


def fabrikant_levels(G, adv_node):
    class FabrikantLeveler(object):
        def __init__(self, G):
            self.G = G
            self.level = {}
            self.sub_nodes = {}

        def levels(self, adv_node):
            self.set_distances_from(adv_node)
            self.trim_sub_nodes()
            return self.level

        def trim_sub_nodes(self):
            for i in sorted(self.sub_nodes.keys(), key=lambda x: self.sub_nodes[x]):
                for j in nx.neighbors(G, i):
                    if j in self.sub_nodes[i]:
                        for z in self.sub_nodes[i].difference(self.sub_nodes[j]):
                            if z != j:
                                # print(f"subnode {z} of {i} had level {self.level[z]}")
                                self.level[z] = min(self.level[z], self.level[i] -1)
                                # print(f"now it has {self.level[z]}")

        def set_distances_from(self, adv_node):
            explored = set()
            self.level[adv_node] = 0
            self.sub_nodes[adv_node] = set()
            to_explore = set([adv_node])

            while len(to_explore) > 0:
                i = to_explore.pop()
                for j in nx.neighbors(G, i):
                    e = G.edges[(i,j)]
                    if e['type'] == 'transit' and str(e['customer']) == i:
                        if j not in self.level:
                            self.level[j] = self.level[i] + 1
                        else:
                            self.level[j] = min(self.level[j], self.level[i]+1)

                        if j not in self.sub_nodes:
                            self.sub_nodes[j] = set()
                        self.sub_nodes[j] = self.sub_nodes[j].union(self.sub_nodes[i])
                        self.sub_nodes[j].add(i)
                        to_explore.add(j)  # there cannot be customer-provider loops

            explored.add(i)

    fl = FabrikantLeveler(G)
    return fl.levels(adv_node)


def strategyfy(G, strategy, adv_node):
    if not adv_node:
        adv_node = list(G.nodes)[-1]
    G.nodes[adv_node]['destinations'] = "10.0.0.0/8"

    if strategy in strategies:
        eval("apply_" + strategy + "_strategy")(G, adv_node)
    else:
        raise ValueError(f"Strategy \"{strategy}\" not available")


if __name__ == "__main__":
    if len(sys.argv) in [3, 4]:
        filename = sys.argv[1]
        strategy = sys.argv[2]

        adv_node = None
        if len(sys.argv) == 4:
            adv_node = sys.argv[3]

        G = nx.read_graphml(filename)
        strategyfy(G, strategy, adv_node)
        nx.write_graphml(G, f"{strategy}_{filename}")
        print(f"Created file {strategy}_{filename} for strategy {strategy}")
    else:
        usage(sys.argv[0])