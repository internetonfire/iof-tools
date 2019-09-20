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
        self.neighs = defaultdict(dict)
        # self.policies?
        self.exportPrefixes = prefixes
        # MRAI da configurare, XdestXneigh
        self.events_memory = []
        self.logging = False

    def setLogging(self, flag):
        self.logging = flag

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
            self.decisionProcess(0, (self.ID, route))
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

    def sendUpdate(self, prefix, neigh, now):
        assert not self.RT[prefix]['SHARED_FLAG'][neigh]
        mrai = self.RT[prefix]['MRAIs'][neigh]
        # mrai scaduto! ready2fire!
        if mrai <= now:
            self.really_send_update(prefix, neigh, now)
        else:
            print("\u001b[31mWait mrai to fire")

    '''really send:
        1. creare l'update e metterlo e farglielo ricevere al vicino
        2. impostare l'MRAI per questa rotta con questo vicino
        3. flaggare la rotta come comunicata a questo vicino'''
    def really_send_update(self, prefix, neigh, now):
        # 1.
        pyneigh = self.neighs[neigh]['pynode']
        rasp = self.RT[prefix]['AS_PATH']
        newAS_PATH = rasp + ',' + self.ID if rasp != "" else self.ID
        rt4update = Route(prefix, {'AS_PATH': newAS_PATH})
        update = (self.ID, rt4update)
        pyneigh.processRXupdates(update, now)
        # 2.
        self.RT[prefix]['MRAIs'][neigh] = now + \
            self.neighs[neigh]['mrai']
        event = {'actor': self.ID, 'action': 'DECISION_PROCESS', 'update': None}
        self.sched.schedule_event(
            self.neighs[neigh]['mrai'] + self.sched.jitter(), event)
        # 3.
        self.RT[prefix]['SHARED_FLAG'][neigh] = True

    def processRXupdates(self, update, now):
        self.log(EventLog(now, 'RECEPTION', update[0],
                          update[1].prefix, update[1].as_path()))
        # Processing, by model, takes non-zero time. This is why I
        # schedule a decision process after short-time
        addj = 0
        if self.ID.startswith('Y'):
            addj=0.001
        event = {'actor': self.ID,
                 'action': 'DECISION_PROCESS', 'update': update}
        self.sched.schedule_event(addj+self.sched.jitter(), event)

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

    def decisionProcess(self, now, update=None):
        # HARD CODING!!! so che ho solo una destinazione nella RT
        prefix = update[1].prefix if update else list(self.RT.adjRIBin.keys())[0]
        if update:
            self.RT.update_adjRIBin(update)
            # Phase 1,2: compute preferences, then select&install the best
            best_rt, learned_by, max_pref, = None, None, float('-inf')
            for sender, route in self.RT.adjRIBin[prefix].items():
                rt_preference = policy(self.ID, route)
                if rt_preference > max_pref:
                    best_rt, learned_by, max_pref = route, sender, rt_preference
            self.RT.install_route(best_rt, learned_by, max_pref, now)
        self.disseminate(prefix, now)

    def disseminate(self, prefix, now):
        for neigh in self.neighs:
            if not self.RT[prefix]['SHARED_FLAG'][neigh]:
                myNeighIsMy = self.neighs[neigh]['relation']
                # policy propagazione update in base a relazioni tra nodi e loro tipo...
                if myNeighIsMy == 'customer':
                    '''Da implementare anche, in futuro, la propagazione
                    nei seguenti casi:
                    - se ho imparato la rotta da un provider OR peer ==> manda ai miei customer
                    - se mi arriva da un customer ==> manda a tutti tranne a chi me l'ha mandata'''
                    self.sendUpdate(prefix, neigh, now)
