from util.event_log import EventLog
from collections import defaultdict
from prettytable import PrettyTable
import code  # code.interact(local=dict(globals(), **locals()))


class Route(object):

    def __init__(self, prefix, attr={}):
        self.prefix = prefix
        self. attr = attr

    def as_path(self):
        return self.attr['AS_PATH']


class RoutingTable(object):

    def __init__(self):
        self.rt = {}
        self.__flag_change = False
        pass

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
                       ['NH'], self.rt[p]['PREFERENCE']])
        print(s)

    def install_route(self, route, sender, route_preference, time):
        prefix, NH, as_path, preference = route.prefix, sender, route.as_path(), route_preference
        new_route = route.prefix not in self.rt
        self.rt[prefix] = {'NH': NH, 'AS_PATH': as_path,
                           'PREFERENCE': preference}
        if new_route:

            self.rt[route.prefix]['MRAIs'] = defaultdict(int)
            self.rt[route.prefix]['SHARED_FLAG'] = defaultdict(
                bool)  # chiavi nuove nascono con valore False
            for neigh in self.neighs:
                # virtualmente scaduto! :)
                self.rt[route.prefix]['MRAIs'][neigh] = time
        else:
            # non modifico l'MRAI pre-esistente, aspetto che scada...
            # ma setto shared_flag = False per tutti, perchè con nessuno
            # ho gia condiviso la nuova rotta appena installata
            self.rt[route.prefix]['SHARED_FLAG'] = defaultdict(
                bool)  # chiavi nuove nascono con valore False
            self.rt[route.prefix]['PREFERENCE'] = preference
        #code.interact(local=dict(globals(), **locals()))
