import ipaddress
from constants import *
import os.path


class Node:
    nodeIpAddr_network = ipaddress.ip_network(u'200.0.0.0/8')
    counter_node = 1
    nodeIpNetworks_network = list(ipaddress.ip_network(u'100.0.0.0/8').subnets(new_prefix=24))
    counter_networks = 1

    def __init__(self, name, out_folder):
        self.name = name
        self.outFolder = out_folder
        self.mainOutFileName = "bgp_h_" + str(self.name) + ".conf"
        self.sessionExporterFile_name = "bgpSessionExporter_h_" + str(name) + ".conf"
        if Node.counter_node < Node.nodeIpAddr_network.num_addresses - 1:
            self.router_addr = Node.nodeIpAddr_network[Node.counter_node]
            Node.counter_node += 1
        else:
            raise ValueError('No more addresses for routers')

        # Templates bases
        with open(BIRD_TEMPLATE_PATH, "r") as bird_file:
            self.bird_template = bird_file.read()
        with open(BGP_SESSION_EXPORTER_TEMPLATE_PATH, "r") as bgp_file:
            self.bgp_session_exporter = bgp_file.read()

        self.mainOutFile = open(self.outFolder + self.mainOutFileName, 'w+')
        self.sessionExporterFile = None
        self.exporting_proto_name = "static_bgp_h_" + str(self.name)
        self.exportedNetworks = []
        self.exportedNetworks_str = ""
        self.log_file_name = "log_h_" + str(self.name) + ".log"

        self.eth_dict = {}

        self.write_main_file()

    def __str__(self):
        return "{" + str(self.name) + "," + str(self.router_addr) + "}"

    def add_addr_to_export(self):
        if Node.counter_networks < len(Node.nodeIpNetworks_network):
            self.exportedNetworks.append(Node.nodeIpNetworks_network[Node.counter_networks])
            Node.counter_networks += 1
        else:
            raise ValueError('No more networks free')
        self.delete_export_file()

        self.exportedNetworks_str += "route " + str(self.exportedNetworks[-1]) + "via \"lo\";\n\t\t\t"

        self.write_export_file()
        self.include_in_main(self.sessionExporterFile_name)

    def write_main_file(self):
        # Write the template inside the file
        open(self.outFolder + self.log_file_name, "a").close()
        self.mainOutFile.write(
            self.bird_template.format(log_file_path=self.log_file_name, log_mode=LOG_MODE, dbg_mode=DBG_MODE,
                                                         dbg_commands_mode=DBG_COMMANDS_MODE, addr=self.router_addr,
                                                         kernel_conf_path=KERNEL_CONF_PATH,
                                                         direct_conf_path=DIRECT_CONF_PATH,
                                                         device_conf_path=DEVICE_CONF_PATH,
                                                         filter_conf_path=FILTER_CONF_PATH,
                                                         bgp_session_export_path="", bgp_session_path=""))

    def delete_export_file(self):
        if os.path.isfile(self.outFolder + self.sessionExporterFile_name):
            os.remove(self.outFolder + self.sessionExporterFile_name)

    def write_export_file(self):
        self.sessionExporterFile = open(self.outFolder + self.sessionExporterFile_name, "w+")
        self.sessionExporterFile.write(self.bgp_session_exporter.format(session_protocol_name=self.exporting_proto_name,
                                                                        addr_to_export=self.exportedNetworks_str))

    def include_in_main(self, file_name):
        self.mainOutFile.write("include  \"" + file_name + "\";\n")

    def set_new_external_addr(self, network, addr):
        self.eth_dict[str(network)] = addr
