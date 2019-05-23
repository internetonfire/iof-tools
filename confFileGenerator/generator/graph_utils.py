#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import networkx as nx

def loadGraph(fname, remap=False, connected=True, silent=False):
    """ Parameters
    --------------
    fname : string
        filname to open
    remap : bool
        remap the labels to a sequence of integers
    connected : bool
        return only the larges component subgraph

    """
    G = nx.Graph() #Creo un grafo
    if not silent:
        print "Loading/Generating Graph" #Messaggio di caricamento per l'utente
    # load a file using networkX adjacency matrix structure
    if fname.lower().endswith(".adj"): #Se il file finisce per adj
        try:
            G = nx.read_adjlist(fname, nodetype=int) #Passo il file alla funzione che legge i file adj
        except IOError as err:
            print
            print err
            sys.exit(1) #In caso di errori stampo un messaggio all'utente
    # load a file using networkX .edges structure
    elif fname.lower().endswith(".edges"):  #Nel caso in cui il file sia .edges
        try:
            G = nx.read_edgelist(fname, nodetype=int,data=(('weight',int),)) #Carico come una lista di edge
        except IOError as err:
            print
            print err
            sys.exit(1) #Stampo un messaggio all'utente
    # load a a network in NetJSON format
    elif fname.lower().endswith(".json"):   #Nel cso in cui sia un file json utilizzo la funzione scritta sopra
        try:
            G = load_json(fname)
        except IOError as err:
            print
            print err
            sys.exit(1)
    else:
        print >> sys.stderr, "Error: Allowed file extensions are .adj for",\
            "adjacency matrix, .json for netjson and .edges for edge-list"  #Nel caso in cui non riesca a trovare il formato del file stampo il messaggio
        sys.exit(1)
    if connected:
        C = sorted(list(nx.connected_component_subgraphs(G)),key=len, reverse=True)[0]    #Ottengo la prima componente connessa
        G = C
    if not silent:
        print >> sys.stderr, "Graph", fname, "loaded\n",   #Messaggio all'utente
    # remap node labels so we don't have "holes" in the numbering
    if remap:
        mapping = dict(zip(G.nodes(), range(G.order())))    #Creo una mappa del grafo
        H = nx.relabel_nodes(G, mapping)
        return H
    return G    #Restituisco il grafo
