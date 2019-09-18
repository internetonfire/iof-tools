class EventLog(object):

    def __init__(self, time, evType, evFrom, prefix, as_path, binPref='ND'):
        self.time = time
        self.evType = evType
        self.evFrom = evFrom
        self.prefix = prefix
        self.as_path = as_path
        self.binPref = binPref

    def to_dict(self):
        return self.__dict__