from util.routing_table import RoutingTable as RT
from util.routing_table import Route
from util.myqueue import MyQueue as MyQueue
from collections import defaultdict
from prettytable import PrettyTable
from policy import policy
import json
import code  # code.interact(local=dict(globals(), **locals()))
from util.event_log import EventLog


class Node(object):

    def __init__(self, node_id, sim_dir, sched, node_type='C', prefixes=[]):
        self.sim_dir = sim_dir
        self.ID = node_id
        self.sched = sched
        self.nodeType = node_type
        self.RT = RT(self)
        self.rxQueue = MyQueue()
        self.neighs = defaultdict(dict)
        # self.policies?
        self.exportPrefixes = prefixes
        # MRAI da configurare, XdestXneigh
        self.events_memory = []
        self.logging=False
        self.configure()

    def setLogging(self, flag):
        self.logging=flag

    '''
    Configure ha 3 compiti:
    1. Far capire alla RT chi siano i vicini del nodo, per poter
    settare gli MRAI x-VICINO, x-destinazione
    2. Mettere in canna i primi update da mandare, 
      relativi ai prefissi esportati da questo nodo.
      Trucco: si mettono gli exportPrefix inizialmente
      nella coda di ricezione
    3. inizializzare il file log (csv|json)?
    '''

    def configure(self):
        # far conoscere a RT i negihbour
        self.RT.set_neighbours(self.neighs)
        # autoricezione prefissi da esportare
        for prefix in self.exportPrefixes:
            route = Route(prefix, {'AS_PATH': ''})
            self_update = (self.ID, route)
            self.rxQueue.push(self_update)
        # apertura file di log
        self.logfile = open(self.sim_dir + "/" + self.ID + "_log.csv", 'a')
        self.logfile.write("TIME|EVENT_TYPE|FROM|PREFIX|AS_PATH|BINPREF"+'\n')

    def toString(self):
        s = PrettyTable()
        s.field_names = ["nID", "nTYPE", "NEIGHS", "expPREFIX"]
        neighPrint = {}
        for n in self.neighs:
            neighPrint[n] = {}
            for k, v in self.neighs[n].items():
                if k in ['relation', 'mrai']:
                    neighPrint[n][k] = v
        s.add_row([self.ID, self.nodeType, '\n'.join(
            map(str, neighPrint.items())), ('\n').join(self.exportPrefixes)])
        print(s)

    def log(self, evlog):
        if not self.logging:
            return
        self.events_memory.append(evlog)
        #to_write = json.dumps(event_describer)
        self.logfile.write('|'.join([str(evlog.time), evlog.evType, evlog.evFrom,
                                     evlog.prefix, evlog.as_path, evlog.binPref])+'\n')
        self.logfile.flush()

        '''
        - route da annunciare
        - vicino a cui mandiamo l'annuncio
        '''

    def sendUpdate(self, prefix, neigh, time):
        try:
            if self.RT[prefix]['SHARED_FLAG'][neigh]:
                return
        except:
            code.interact(local=dict(globals(), **locals()))
        mrai = self.RT[prefix]['MRAIs'][neigh]
        if mrai <= time:  # mrai scaduto! ready2fire!
            self.really_send_update(prefix, neigh, time)
        else:
            print("\u001b[31mWait mrai to fire")

    def really_send_update(self, prefix, neigh, time):
        '''really send:
        1. creare l'update e metterlo nel bufferRX del vicino
        2. impostare l'MRAI per questa rotta con questo vicino
        3. flaggare la rotta come comunicata a questo vicino'''
        # 1.
        pyneigh = self.neighs[neigh]['pynode']
        rt4update = Route(prefix, {})
        rasp = self.RT[prefix]['AS_PATH']
        newAS_PATH = rasp + ',' + self.ID if rasp != "" else self.ID
        rt4update.attr['AS_PATH'] = newAS_PATH
        update = (self.ID, rt4update)
        pyneigh.rxQueue.push(update)
        self.sched.schedule_event(
            1.0 + self.sched.jitter(), {'actor': neigh, 'action': 'CHECK_RX'})
        # 2.
        self.RT[prefix]['MRAIs'][neigh] = time + \
            self.neighs[neigh]['mrai']
        event = {'actor': self.ID, 'action': 'MRAI_DEADLINE',
                 'prefix': prefix, 'neigh': neigh}
        
        self.sched.schedule_event(
            self.neighs[neigh]['mrai'] + self.sched.jitter(positive=True), event)
        # 3.
        self.RT[prefix]['SHARED_FLAG'][neigh] = True

    def processRXupdates(self, time):
        while not self.rxQueue.isEmpty():
            update = self.rxQueue.pop()
            self.log(EventLog(time, 'UpdateRX', update[0],
                              update[1].prefix, update[1].as_path()))
            self.RT.update_adjRIBin(update)
        self.selectInstall(time)

    '''Da BGP RFC`
    The Decision Process takes place in three distinct phases, each
    triggered by a different event:
    a) Phase 1 is responsible for calculating the degree of preference
    for each route received from a peer.
    b) Phase 2 is invoked on completion of phase 1. It is responsible
    for choosing the best route out of all those available for each
    distinct destination, and for installing each chosen route into
    the Loc-RIB.
    c) Phase 3 is invoked after the Loc-RIB has been modified. It is
    responsible for disseminating routes in the Loc-RIB to each
    peer, according to the policies contained in the PIB. Route
    aggregation and information reduction can optionally be
    performed within this phase.
    '''

    def selectInstall(self, time):
        #code.interact(local=dict(globals(), **locals()))
        prefix = list(self.RT.adjRIBin.keys())[0]
        # Phase 1,2: compute preferences, then select&install the best
        best_rt, learned_by, max_pref, = None, None, float('-inf')
        for sender, route in self.RT.adjRIBin[prefix].items():
            rt_preference = policy(self.ID, route)
            if rt_preference > max_pref:
                best_rt, learned_by, max_pref = route, sender, rt_preference
        self.RT.install_route(best_rt, learned_by, max_pref, time)

        # Phase 3: routes dissemination
        for neigh in self.neighs:
            if not self.RT[prefix]['SHARED_FLAG'][neigh]:
                myNeighIsMy = self.neighs[neigh]['relation']
                # policy propagazione update in base a relazioni tra nodi e loro tipo...
                if myNeighIsMy == 'customer':
                    '''Da implementare anche, in futuro, la propgazione
                    nei seguenti casi:
                    - se ho imparato la rotta da un provider OR peer ==> manda ai miei customer
                    - se mi arriva da un customer ==> manda a tutti tranne a chi me l'ha mandata'''
                    self.sendUpdate(prefix, neigh, time)
