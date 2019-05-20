#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import sys
import networkx as nx


def load_json(json_file): #Caricamento del grafico da file json
    """ import a json file in NetJSON format, convert to Graph class
    Parameters
    ----------
    json_file : string with file path
    """
    #Carico il json
    try:
        file_p = open(json_file, "r")
    except IOError:
        raise
    try:
        netjson_net = json.load(file_p)
    except ValueError as err:
        print "Could not decode file", err
    # TODO add a schema to validate the subset of features we are
    # able to consider

    G = nx.Graph()
    cost_label = ""
    if "metric" in netjson_net and netjson_net["metric"] == "ETX":
        cost_label = "cost"
    for node in netjson_net["nodes"]:
        G.add_node(node["id"])
    for link in netjson_net["links"]:
        if cost_label:
            cost = float(link["cost"])
        else:
            cost = 1.0
        G.add_edge(link["source"], link["target"], attr_dict={"weight": cost}) #Aggiungo il nodo con i propri link ed il costo
    return G #Restituisco il grafico


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
