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
        print("InitNodes")
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

    def scedule_initial_events(self, sched):
        for nodeID in self.nodes:
            if self.nodes[nodeID].exportPrefixes:
                sched.schedule_event(0.1 + sched.jitter(),
                                 {'actor': nodeID, 'action': 'CHECK_RX'})

    def runSimulation(self):
        sched = self.sched
        print("Simulation started")
        time = 0
        with tqdm(total=MAX_DURATION) as pbar:
            while(sched.elapsed_time() < MAX_DURATION and len(sched.queue) > 0):
                event = sched.pop_event()
                current_time = sched.elapsed_time()
                node = self.nodes[event['actor']]
                if event['action'] == 'CHECK_RX':
                    node.processRXupdates(sched.elapsed_time())
                    # reschedule same event of type 'CHECK_RX'
                    # sched.schedule_event(1.0 + sched.jitter(), event)
                elif event['action'] == 'MRAI_DEADLINE':
                    node.sendUpdate(
                        event['prefix'], event['neigh'], sched.elapsed_time())
                sleep(0.05)
                time += 10
                pbar.update(sched.step())


def config_out_path(outPath, graphName):
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
    sim.scedule_initial_events(sim.sched)
    sim.runSimulation()
    print("FINISHED SIMULATION, MAX TIME OR CONVERGENCE REACHED")
    for n in sim.nodes.values():
        print("RT of NODE: "+n.ID)
        n.RT.dumps()

    time = sim.sched.elapsed_time()
    x1 = sim.nodes['X1']
    prefix = x1.exportPrefixes[0]
    route = Route(prefix, {'AS_PATH': 'P'})
    x1.RT.install_route(route, x1.ID, 1, time)
    for neigh in x1.neighs:
        event = {'actor': x1.ID, 'action': 'MRAI_DEADLINE',
                 'prefix': prefix, 'neigh': neigh}
        sim.sched.schedule_event(
            16 + x1.neighs[neigh]['mrai'] + sim.sched.jitter(positive=True), event)
    print("RESTARTED SIMULATION AFTER LINK FAILURE SIM")
    for node in sim.nodes.values():
        node.setLogging(True)
    sim.runSimulation()
    #code.interact(local=dict(globals(), **locals()))
    print("FINISHED AGAIN SIMULATION...")
    for n in sim.nodes.values():
        print("RT of NODE: "+n.ID)
        n.RT.dumps()
