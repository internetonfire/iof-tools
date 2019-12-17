from prettytable import PrettyTable
import numpy as np
import networkx as nx 
import random as rnd
import matplotlib.pyplot as plt

import matplotlib.colors as mcolors
import sys
import code  # code.interact(local=dict(globals(), **locals()))

def draw(G, pos, xmax, ymax, measures=None, saveFig=False, path=None):
    fig = plt.figure()
    lay = {k:pos[k] for k in range(0,len(pos))}
    if not measures:
        measures = nx.betweenness_centrality(G, normalized = True, weight = 'weight', endpoints=True)

    measure_name = "Betweenness"

    nodes = nx.draw_networkx_nodes(G, lay, node_size=50, cmap=plt.cm.Spectral, 
                                       node_color=measures.values(),
                                       nodelist=measures.keys())

    #nodes.set_norm(mcolors.SymLogNorm(linthresh=0.01, linscale=1))
    mes=measures.values()
    nodes.set_norm(mcolors.LogNorm(vmin=0.001, vmax=max(mes)))
    #nodes.set_norm(mcolors.LogNorm())

    edges = nx.draw_networkx_edges(G, lay)
    plt.title(measure_name)

    myticks=np.geomspace(start=0.001, stop=max(mes), num=7)
    cbar=plt.colorbar(nodes, ticks=myticks, label='Norm BC')
    cbar.ax.set_yticklabels(["{0:0.4f}".format(i) for i in myticks])
    #plt.colorbar(ticks=range(6), label='digit value')
    #plt.clim(-0.5, 5.5)
    plt.xlim(0, xmax)
    plt.ylim(0, ymax)
    plt.xticks(range(0,105,5))
    plt.yticks(range(0,105,5))
    plt.grid(which='both')
    if not saveFig:
        plt.ion()
        plt.draw()
        plt.pause(0.01)
        plt.clf()
    else:
        fig.savefig(path, format='pdf')
        #plt.clf()
        #plt.show()

def dictAlikes(d1, d2, perc):
	if (sorted(d1.keys()) != sorted(d2.keys())):
		return False
	for k in d1:
		a = float(d1[k])
		b = float(d2[k])
		if (not b - (b*perc) <= a <= b + (b*perc)):
			return False
	return True

def summary(v):
    vmin=min(v)
    vmax=max(v)
    tot=sum(v)
    avg=np.mean(v)
    std=np.std(v)
    t = PrettyTable(['min','max', 'mean','std','tot'])
    s = "%.4f %.4f %.4f %.4f %.4f" % (vmin,vmax,avg,std,tot)
    t.add_row(s.split())
    print t
    return avg, std, vmax, vmin, tot