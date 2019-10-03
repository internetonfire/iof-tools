from util.event_log import EventLog
from collections import defaultdict
from prettytable import PrettyTable
import code  # code.interact(local=dict(globals(), **locals()))


class Route(object):

    def __init__(self, prefix, attr={}):
        self.prefix = prefix
        self. attr = attr

    def __str__(self):
        return "<"+self.prefix+", "+str(self.attr)+">"

    def as_path(self):
        return self.attr['AS_PATH']


class RoutingTable(object):

    def __init__(self, node):
        self.rt = defaultdict(dict)
        self.adjRIBin = defaultdict(dict)
        self.node = node

    def __contains__(self, key):
        return key in self.rt

    def __getitem__(self, key):
        return self.rt[key]

    def __setitem__(self, key, value):
        self.rt[key] = value

    def set_neighbours(self, neighs):
        self.neighs = neighs

    def dumps(self):
        s = PrettyTable()
        s.field_names = ["PREFIX", "AS_PATH", "NH", "PREFERENCE"]
        for p in self.rt:
            s.add_row([p, self.rt[p]['AS_PATH'], self.rt[p]
                       ['NH'], bin(self.rt[p]['PREFERENCE'])[2:]])
        print(s)

    def update_adjRIBin(self, update):
        sender, route = update
        self.adjRIBin[route.prefix][sender] = route

    def install_route(self, route, sender, rt_preference, time):
        prefix, NH, as_path, preference = route.prefix, sender, route.as_path(), rt_preference
        new_route = prefix not in self.rt
        modified=False
        old_best = self.rt[prefix]['AS_PATH'] if not new_route else None
        if not new_route:
            entry = self.rt[prefix]
            modified = (NH, as_path, preference) != (entry['NH'], entry['AS_PATH'], entry['PREFERENCE'])
            #if modified and self.node.ID=='X4':
            #    code.interact(local=dict(globals(), **locals()))
        self.rt[prefix].update({'NH': NH, 'AS_PATH': as_path,
                                'PREFERENCE': preference
                                })
        if new_route:
            self.rt[prefix]['MRAIs'] = {}
            for neigh in self.neighs:
                # virtualmente scaduto! :)
                self.rt[prefix]['MRAIs'][neigh] = time
        if new_route or modified:
            # print("\tINSTALLED",prefix,"with AS_PATH",as_path)
            # non modifico l'MRAI pre-esistente, aspetto che scada...
            # ma setto shared_flag = False per tutti, perchè con nessuno
            # ho gia condiviso la nuova rotta appena installata
            self.rt[prefix]['SHARED_FLAG'] = defaultdict(bool)
            # self.node.log(EventLog(time, 'INSTALLED_ROUTE', NH,
            #                       prefix, as_path, bin(preference)[2:]))
        new_best_path = self.rt[prefix]['AS_PATH']
