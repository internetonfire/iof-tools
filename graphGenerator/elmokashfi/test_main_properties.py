#!/usr/bin/env python3
import os
import urllib.request
import networkx as nx
import sys
import collections
import matplotlib.pyplot as plt
import tarfile
import shutil


def retrieve_as_graph():
    filename = 'as-caida20070917.txt'
    if not os.path.isfile(filename):
        urllib.request.urlretrieve('https://snap.stanford.edu/data/as-caida.tar.gz', 'caida.tar.gz')

        tar = tarfile.open("caida.tar.gz")
        tar.extractall()
        tar.close()
    H = nx.read_weighted_edgelist(filename, create_using=nx.DiGraph)
    H = nx.Graph(H)
    return (H, f"Internet-{len(H.nodes())}")


def generate_graph(nodes):
    filename = f"baseline-{nodes}.graphml"
    if not os.path.isfile(filename):
        if os.path.isfile("bgp.py"):
            import bgp as bgp
        else:
            import networkx as bgp

        G = bgp.internet_as_graph(nodes)
        nx.write_graphml(G, filename)
    else:
        G = nx.read_graphml(filename)
    G = nx.Graph(G)
    return (G, f"Baseline-{len(G.nodes())}")


def check_hierarchical_structure(G):
    E = []
    for e in G.edges:
        if G.edges[e]['type'] == 'transit':
            E.append(e)
    DG = nx.DiGraph()
    for e in E:
        DG.add_edge(e[1], e[0])

    cycles = list(nx.simple_cycles(DG))
    if len(cycles) == 0:
        return True
    else:
        return False


def line2point(d1):
    x = []
    y = []
    last = None
    for e in range(len(d1)):
        if not last or last != d1[e]:
            x.append(e+1)
            y.append(d1[e])
            last = d1[e]
    return (x, y)
        

def log_log_plot(d1, l1, d2, l2, filename):
    x, y = line2point(d1)
    plt.plot(x, y, 'o', color='blue', lw=2, label=l1)
    x, y = line2point(d2)
    plt.plot(x, y, 'x', color='red', lw=2, label=l2)
    plt.yscale('log')
    plt.xscale('log')
    plt.legend()
    plt.savefig(filename)


def degree_freqs(G):
    x = []
    degree_sequence = sorted([d for n, d in G.degree()], reverse=True)  
    M = degree_sequence[0]  # maximum
    degreeCount = collections.Counter(degree_sequence)
    for i in range(1, M+1):
        if i in degreeCount:
            x.append(degreeCount[i])
        else:
            x.append(0)
    return x


def avg_clust_per_degree(G):
    node_clust = nx.clustering(G, weight=None)
    node_degree = G.degree()
    x = []

    degree_look_up = {}
    for n,d in node_degree:
        l = degree_look_up.get(d, [])
        l.append(n)
        degree_look_up[d] = l

    M = max(degree_look_up)  # maximum degree
    for d in range(1, M+1):
        if d in degree_look_up:
            avg = 0
            for n in degree_look_up[d]:
                avg += node_clust[n]
            #avg /= len(degree_look_up[d])
            x.append(avg)
        else:
            x.append(0)
    return x


def norm_avg_neigh_degree(G):
    node_degree = G.degree()
    x = []

    degree_look_up = {}
    for n,d in node_degree:
        l = degree_look_up.get(d, [])
        l.append(n)
        degree_look_up[d] = l

    M = max(degree_look_up)  # maximum degree
    for d in range(1, M+1):
        if d in degree_look_up:
            avg = 0
            for n in degree_look_up[d]:
                n_avg = 0
                n_neigh = 0
                for neigh in nx.neighbors(G, n):
                    n_avg += node_degree[neigh]
                    n_neigh += 1
                n_avg /= n_neigh

                avg += n_avg

            avg /= len(degree_look_up[d])
            x.append(avg)
        else:
            x.append(0)

    s = sum(x)
    x = [i/s for i in x]
    return x


def ccdf_from_freqs(freqs):
    res = []
    s = sum(freqs)
    freqs = [f/s for f in freqs]
    s = 0
    for f in freqs:
        res.append(1-s)
        s += f
    return res


def power_law_analysis(G, Gname, H, Hname):
    df1 = degree_freqs(G)
    df2 = degree_freqs(H)
    df1 = ccdf_from_freqs(df1)
    df2 = ccdf_from_freqs(df2)

    plt.figure()
    plt.xlabel("Node degree")
    plt.ylabel("CCDF")
    log_log_plot(df1, Gname, df2, Hname, "power_law_analysis.pdf")


def clustering_analysis(G, Gname, H, Hname):
    df1 = avg_clust_per_degree(G)
    df2 = avg_clust_per_degree(H)

    plt.figure()
    plt.xlabel("Node degree")
    plt.ylabel("Local clustering")
    log_log_plot(df1, Gname, df2, Hname, "clustering_analysis.pdf")


def connectivity_analysis(G, Gname, H, Hname):
    df1 = norm_avg_neigh_degree(G)
    df2 = norm_avg_neigh_degree(H)

    plt.figure()
    plt.xlabel("Node degree")
    plt.ylabel("Normalized avg neighbor degree")
    log_log_plot(df1, Gname, df2, Hname, "connectivity_analysis.pdf")


def check_avg_path_length(G, target, eps):
    G2 = nx.Graph(G)  # we make it undirected
    pl = nx.average_shortest_path_length(G2)
    if pl > target - eps and pl < target + eps:
        return True
    else:
        print(f"(PL={round(pl, 2)})", end='')
        return False
  

def print_success():
    print("\033[1;32;40m[OK]\033[0m")


def print_failure():
    print("\033[1;31;40m[FAIL]\033[0m")


if __name__ == "__main__":
    print("Real-world graph retrieving (44.2 MB)...", end='')
    sys.stdout.flush()
    H, Hname = retrieve_as_graph()
    print("[DONE]")

    print("Baseline generation...", end='')
    sys.stdout.flush()
    G, Gname = generate_graph(len(H.nodes()))
    print("[DONE]")

    print("Checking hierarchical structure...", end='')
    sys.stdout.flush()
    if check_hierarchical_structure(G):
        print_success()
    else:
        print_failure()

    print("Generating degree comparison images...", end='')
    sys.stdout.flush()
    power_law_analysis(G, Gname, H, Hname)
    print("[DONE]")

    print("Generating clustering comparison images...", end='')
    sys.stdout.flush()
    clustering_analysis(G, Gname, H, Hname)
    print("[DONE]")

    print("Generating connectivity comparison images...", end='')
    sys.stdout.flush()
    connectivity_analysis(G, Gname, H, Hname)
    print("[DONE]")

    print("Checking average path length...", end='')
    sys.stdout.flush()
    if check_avg_path_length(G, 4, 0.5):
        print_success()
    else:
        print_failure()
