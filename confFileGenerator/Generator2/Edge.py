import ipaddress
from constants import *
import os.path


class Edge:
    nodeIpNetworks_externalEth = list(ipaddress.ip_network(u'10.0.0.0/12').subnets(new_prefix=30))
    counter_external_networks = 1

    def __init__(self, node1, node2, out):
        self.node1 = node1
        self.node2 = node2
        self.outFolder = out

        self.bgpSessionFile1_name = "bgpSession_h_" + str(self.node1.name) + "_h_" + str(self.node2.name) + ".conf"
        self.bgpSessionFile2_name = "bgpSession_h_" + str(self.node2.name) + "_h_" + str(self.node1.name) + ".conf"

        with open(BGP_SESSION_TEMPLATE_PATH, "r") as bgp_file:
            self.bgp_session = bgp_file.read()

        if self.counter_external_networks < len(self.nodeIpNetworks_externalEth):
            self.edge_network = self.nodeIpNetworks_externalEth[self.counter_external_networks]
            self.counter_external_networks += 1
        else:
            raise ValueError('No more networks available for edges')

        self.node1.set_new_external_addr(self.edge_network, self.edge_network[1])
        self.node2.set_new_external_addr(self.edge_network, self.edge_network[2])

        self.del_exporter(self.bgpSessionFile1_name)
        self.del_exporter(self.bgpSessionFile2_name)

        self.bgpSessionFile1 = open(self.outFolder + self.bgpSessionFile1_name, 'w+')
        self.bgpSessionFile2 = open(self.outFolder + self.bgpSessionFile2_name, 'w+')

        self.write_both_session_exporter()

    def __str__(self):
        return str(self.node1) + " <-> " + str(self.node2)

    def del_exporter(self, file_name):
        if os.path.isfile(self.outFolder + file_name):
            os.remove(self.outFolder + file_name)

    def write_both_session_exporter(self):
        self.write_session_exporter(self.bgpSessionFile1, "h_" + str(self.node1.name) + "_" + "h_"
                                    + str(self.node2.name), self.edge_network[1], str(int(self.node1.name) + 1),
                                    self.edge_network[2], str(int(self.node2.name) + 1), str(1))
        self.node1.include_in_main(self.bgpSessionFile1_name)
        self.write_session_exporter(self.bgpSessionFile2, "h_" + str(self.node2.name) + "_" + "h_"
                                    + str(self.node1.name), self.edge_network[2], str(int(self.node2.name) + 1),
                                    self.edge_network[1], str(int(self.node1.name) + 1), str(1))
        self.node2.include_in_main(self.bgpSessionFile2_name)

    def write_session_exporter(self, file, protocol_name, local_addr, local_as, neigh_addr, neigh_as, bgp_local_pref):
        file.write(self.bgp_session.format(protocol_name=protocol_name, local_addr=local_addr,
                                           local_as=local_as, peer_addr=neigh_addr, peer_as=neigh_as,
                                           hold_timer=HOLD_TIMER,
                                           connect_retry_timer=CONNECT_RETRY_TIMER,
                                           connect_delay_timer=CONNECT_DELAY_TIMER,
                                           startup_hold_timer=STARTUP_HOLD_TIMER,
                                           local_pref=bgp_local_pref))
