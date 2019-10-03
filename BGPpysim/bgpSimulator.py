from argparse import ArgumentParser
import networkx as nx
from pprint import pprint
from util.EventScheduler import EventScheduler
from util.node import Node
from time import sleep
from tqdm import tqdm
import random
import sys
import datetime
import os
import shutil
from util.routing_table import Route
import code  # code.interact(local=dict(globals(), **locals()))

MAX_DURATION = 10000


class bgpSim(object):

    def __init__(self, graph, sim_dir):
        self.G = graph
        self.sim_dir = sim_dir
        self.sched = EventScheduler()
        self.initNodes(G)

    def initNodes(self, G):
        # print("InitNodes")
        nodes = {}
        # Node attributes
        for n in self.G.nodes(data=True):
            node_id = n[0]
            node_type, prefixes = 'C', []
            if 'type' in n[1]:
                node_type = n[1]['type']
            if 'destinations' in n[1]:
                prefixes = n[1]['destinations'].split(',')
            nodes[node_id] = Node(node_id, self.sim_dir,
                                  self.sched, node_type, prefixes)

        # Edge attributes
        for e in self.G.edges(data=True):
            #source, target = e[0], e[1]
            edge_type, end1, end2, mrai1, mrai2, customer = e[2]['type'], e[2]['termination1'], e[
                2]['termination2'], float(e[2]['mrai1']), float(e[2]['mrai2']), e[2]['customer']
            if edge_type == 'peer':
                nodes[end1].neighs[end2] = {
                    'relation': 'peer', 'mrai': mrai1, 'pynode': nodes[end2]}
                nodes[end2].neighs[end1] = {
                    'relation': 'peer', 'mrai': mrai2, 'pynode': nodes[end1]}
            elif edge_type == 'transit':
                c, p = (end1, end2) if customer == end1 else (end2, end1)
                p2c, c2p = (mrai1, mrai2) if customer == end1 else (
                    mrai2, mrai1)
                # my neigh is my provider
                nodes[c].neighs[p] = {
                    'relation': 'provider', 'mrai': c2p, 'pynode': nodes[p]}
                # my neigh is my customer
                nodes[p].neighs[c] = {
                    'relation': 'customer', 'mrai': p2c, 'pynode': nodes[c]}
        self.nodes = nodes
        for n in nodes.values():
            n.configure()

    def runSimulation(self):
        sched = self.sched
        print("Simulation started")
        #code.interact(local=dict(globals(), **locals()))
        with tqdm(total=MAX_DURATION) as pbar:
            while sched.elapsed_time() < MAX_DURATION and len(sched.queue) > 0:
                event = sched.pop_event()
                node = self.nodes[event['actor']]
                if event['action'] == 'DECISION_PROCESS':
                    # node.log2("elapsed time: " + str(sched.elapsed_time()) + "\n")
                    node.decisionProcess(sched.elapsed_time(), event['update'])
                pbar.update(sched.step())


def config_out_path(outPath, graphName):
    print(outPath)
    if not os.path.exists(outPath):
        raise Exception("\u001b[31mCannot find the outpath you provided!\n")
    else:
        start = datetime.datetime.now().strftime("%Hh%Mm%Ss_%d-%m-%Y")
        expCode = random.randint(0, 999)
        cdir = outPath + '/' + 'bgpSim_' + \
            graphName + '_' + str(expCode)+'_' + start
        if os.path.exists(cdir):
            shutil.rmtree(cdir)
        os.makedirs(cdir)
        return cdir


if __name__ == '__main__':
    # Define and get required args
    parser = ArgumentParser()
    parser.add_argument("-g", "--graph",
                        dest="graph", required=True, action="store",
                        help="Graph topology describer, .graphml format.")
    parser.add_argument("-w", "--write-to", dest="writeto",
                        default="out/", action="store",
                        help="Output folder for simulation")
    args = parser.parse_args()
    graph_path = args.graph
    graphName = graph_path.split('/')[-1].strip('.graphml')
    output_folder = args.writeto
    sim_dir = config_out_path(output_folder, graphName)

    G = nx.read_graphml(path=graph_path)

    # Initialize simulator and start simulation
    sim = bgpSim(G, sim_dir)
    for node in sim.nodes.values():
        node.setLogging(True)

    sim.runSimulation()
    print("FINISHED SIMULATION, MAX TIME OR CONVERGENCE REACHED")
    # for n in sim.nodes.values():
    #    print("RT of NODE: "+n.ID)
    #    n.RT.dumps()
    
    #code.interact(local=dict(globals(), **locals()))
    time1 = sim.sched.elapsed_time()
    time = time1 + 300

    x1 = sim.nodes['X1']
    prefix = x1.exportPrefixes[0]
    route = Route(prefix, {'AS_PATH': 'P'})
    x1.RT.install_route(route, x1.ID, 1, time)

    event = {'actor': x1.ID, 'action': 'DECISION_PROCESS', 'update': (x1.ID, route)}
    time_with_jitter = time + sim.sched.jitter() - time1
    sim.sched.schedule_event(time_with_jitter, event)
    # x1.log2("il tempo di merda é: " + str(time_with_jitter) + "\n")
    print("RESTARTED SIMULATION AFTER LINK FAILURE SIM")

    tim = x1.start_time + datetime.timedelta(0, time)
    timing = tim.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    x1.log2(timing + " <FATAL> {type: RECONF}\n")

    sim.runSimulation()
    print("FINISHED AGAIN SIMULATION...")
    # for n in sim.nodes.values():
    #    print("RT of NODE: "+n.ID)
    #    n.RT.dumps()
