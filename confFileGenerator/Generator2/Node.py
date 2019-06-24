import ipaddress


class Node:
    nodeIpAddr_network = ipaddress.ip_network(u'200.0.0.0/8')
    counter = 1

    def __init__(self, name):
        self.name = name
        self.mainOutFile = "bgp_h_" + str(name) + ".conf"
        self.sessionExporterFile = "bgpSessionExporter_h_" + str(name) + ".conf"
        if Node.counter < Node.nodeIpAddr_network.num_addresses - 1:
            self.router_addr = Node.nodeIpAddr_network[Node.counter]
            Node.counter += 1
        else:
            raise ValueError('No more addresses for routers')

    def __str__(self):
        return str(self.name + " " + str(self.router_addr))
