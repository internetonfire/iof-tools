import ipaddress
from constants import *
import os.path


class Edge:
    nodeIpNetworks_externalEth = list(ipaddress.ip_network(u'10.0.0.0/12').subnets(new_prefix=30))
    counter_external_networks = 1

    def __init__(self, node1, node2, type, out):
        self.node1 = node1
        self.node2 = node2
        self.type = type
        self.outFolder = out

        self.bgpSessionFile1_name = "bgpSession_h_" + str(self.node1.name) + "_h_" + str(self.node2.name) + ".conf"
        self.bgpSessionFile2_name = "bgpSession_h_" + str(self.node2.name) + "_h_" + str(self.node1.name) + ".conf"

        with open(BGP_SESSION_EXPORTER_TEMPLATE_PATH, "r") as bgp_file:
            self.bgp_session = bgp_file.read()
        with open(BGP_SESSION_STATIC_EXPORTER_TEMPLATE_PATH, "r") as bgp_file:
            self.bgp_session_static = bgp_file.read()

        if self.counter_external_networks < len(self.nodeIpNetworks_externalEth):
            self.edge_network = self.nodeIpNetworks_externalEth[self.counter_external_networks]
            self.counter_external_networks += 1
        else:
            raise ValueError('No more networks available for edges')

        self.node1.set_new_external_addr(self.edge_network, self.edge_network[1])
        self.node2.set_new_external_addr(self.edge_network, self.edge_network[2])

        if self.type == "transit":
            self.node1.add_servicer(self.node2)
            self.node2.add_customer(self.node1)
        elif self.type == "peer":
            self.node1.add_peer(self.node2)
            self.node2.add_peer(self.node1)
        else:
            raise ValueError("Type not correct, it's possible to use only transit and peer")

        self.bgpSessionFile1 = open(self.outFolder + self.bgpSessionFile1_name, 'w+')
        self.bgpSessionFile2 = open(self.outFolder + self.bgpSessionFile2_name, 'w+')

    def __str__(self):
        return str(self.node1) + " <-> " + str(self.node2)

    def write_static_exporter(self):
        node1_exported = ""
        node2_exported = ""
        if self.type == "transit":
            # I'm the customer in the edge, so if I receive something I have to send the info to only my customers
            node1_exported = self.node1.require_exported("c")
            # I'm the servicer in the edge, so if I receive something I have to send to all my connected nodes, except for the customer that sended to me the info
            node2_exported = self.node2.require_exported("s", sender=self.node1)
        if self.type == "peer":
            node1_exported = self.node1.require_exported("p")
            node2_exported = self.node2.require_exported("p")

        self.write_session_static_exporter(self.bgpSessionFile1, "h_" + str(self.node1.name) + "_" + "h_"
                                           + str(self.node2.name), self.edge_network[1], str(int(self.node1.name) + 1),
                                           self.edge_network[2], str(int(self.node2.name) + 1), node1_exported, str(1))
        self.node1.include_in_main(self.bgpSessionFile1_name)
        if self.type != "peer":
            self.write_session_static_exporter(self.bgpSessionFile2, "h_" + str(self.node2.name) + "_" + "h_"
                                               + str(self.node1.name), self.edge_network[2], str(int(self.node2.name) + 1),
                                               self.edge_network[1], str(int(self.node1.name) + 1), node2_exported, str(1))
            self.node2.include_in_main(self.bgpSessionFile2_name)

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

    def write_session_static_exporter(self, file, protocol_name, local_addr, local_as, neigh_addr, neigh_as,
                                      export_list, bgp_local_pref):
        file.write(self.bgp_session_static.format(protocol_name=protocol_name, local_addr=local_addr,
                                           local_as=local_as, peer_addr=neigh_addr, peer_as=neigh_as,
                                           hold_timer=HOLD_TIMER, export_protocol=export_list,
                                           connect_retry_timer=CONNECT_RETRY_TIMER,
                                           connect_delay_timer=CONNECT_DELAY_TIMER,
                                           startup_hold_timer=STARTUP_HOLD_TIMER,
                                           local_pref=bgp_local_pref))
