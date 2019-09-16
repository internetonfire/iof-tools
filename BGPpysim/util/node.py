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

    def __init__(self, node_id, sim_dir, node_type='C', prefixes=[]):
        self.sim_dir = sim_dir
        self.ID = node_id
        self.nodeType = node_type
        self.RT = RT()
        self.rxQueue = MyQueue()
        self.neighs = defaultdict(dict)
        # self.policies?
        self.exportPrefixes = prefixes
        # MRAI da configurare, XdestXneigh
        self.events_memory = []
        self.configure()

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
        self.logfile.write("TIME|EVENT_TYPE|FROM|PREFIX|AS_PATH"+'\n')

    def toString(self):
        s = PrettyTable()
        s.field_names = ["nID", "nTYPE", "NEIGHS", "expPREFIX"]
        neighPrint = {}
        for n in self.neighs:
            neighPrint[n]={}
            for k,v in self.neighs[n].items():
                if k in ['relation', 'mrai']:
                    neighPrint[n][k]=v
        s.add_row([self.ID, self.nodeType, '\n'.join(
            map(str, neighPrint.items())), ('\n').join(self.exportPrefixes)])
        print(s)

    def log(self, evlog):
        self.events_memory.append(evlog)
        #to_write = json.dumps(event_describer)
        self.logfile.write('|'.join([str(evlog.time), evlog.evType, evlog.evFrom,
                                     evlog.prefix, evlog.as_path])+'\n')

        '''
        - route da annunciare
        - vicino a cui mandiamo l'annuncio
        '''

    def sendUpdate(self, route, neigh, time):
        #print(self.ID, ": sending Update")
        try:
            mrai = self.RT[route.prefix]['MRAIs'][neigh]
            if mrai <= time:  # mrai scaduto! ready2fire!
                self.really_send_update(route, neigh, time)
            else:
                pass  # just wait mrai to fire
        except KeyError:
            # MRAIs for the couple (prefix, neigh) not found!
            # assenza di MRAI per (prefix, neigh) ==> ready2fire
            raise Exception("\u001b[31m"+self.ID +
                            ": mrai not found for neigh "+neigh)

    def really_send_update(self, route, neigh, time):
        '''really send:
        1. mettere l'update nel bufferRX del vicino
        2. impostare l'MRAI per questa rotta con questo vicino
        3. flaggare la rotta come comunicata a questo vicino'''
        # 1.
        pyneigh = self.neighs[neigh]['pynode']
        rt4update = Route(route.prefix, {})
        rasp = route.as_path()
        newAS_PATH = rasp + ',' + self.ID if rasp != "" else self.ID 
        rt4update.attr['AS_PATH'] = newAS_PATH
        update = (self.ID, rt4update)
        pyneigh.rxQueue.push(update)
        # 2. and 3.
        self.RT[route.prefix]['MRAIs'][neigh] = time + self.neighs[neigh]['mrai']
        self.RT[route.prefix]['SHARED_FLAG'][neigh] = True

    def processRXupdates(self, time):
        #print(self.ID, ": processing Received Updates")
        while not self.rxQueue.isEmpty():
            update = self.rxQueue.pop()
            self.log(EventLog(time, 'UpdateRX', update[0],
                              update[1].prefix, update[1].as_path()))
            self.processUpdate(update, time)

    def processUpdate(self, update, time):
        sender, route = update
        route_preference = policy(self.ID, route)

        # Standard Bellman-Ford to update RT
        if route.prefix not in self.RT:
            self.RT.install_route(route, sender, route_preference, time)
        elif route.prefix in self.RT:
            current_preference = self.RT[route.prefix]['PREFERENCE']
            if route_preference > current_preference:
                self.RT.install_route(route, sender, route_preference, time)
            '''ATTENZIONE:
            da capire come gestire withdraw o un peggioramento della preference da parte dello stesso
            vicino (tipo cambio path offerto!) Qui bisogna triggerare l'installazione delle backup-routes '''

        # Capire se ci sono aggiornamenti da propagare
        for neigh in self.neighs:
            myNeighIsMy = self.neighs[neigh]['relation']
            # vuol dire non gliela ho comunicata
            if self.RT[route.prefix]['SHARED_FLAG'][neigh] == False:
                # policy propagazione update in base a relazioni tra nodi e loro tipo...
                if myNeighIsMy == 'customer':
                    '''Da implementare anche, in futuro, la propgazione
                    nei seguenti casi:
                    - se ho imparato la rotta da un provider OR peer ==> manda ai miei customer
                    - se mi arriva da un customer ==> manda a tutti tranne a chi me l'ha mandata'''
                    self.sendUpdate(route, neigh, time)
