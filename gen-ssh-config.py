#!/usr/bin/env python
import xml.etree.ElementTree as ET
from argparse import ArgumentParser
import sys
from ssh_config_template import SSHConfig

from const import COMPONENT_ID, NODE, SSH_CONFIG_TEMPLATE, \
    HOST_CONFIG_TEMPLATE, IDENTITY_FILE, NODE_NAME

parser = ArgumentParser()
parser.add_argument("-r", "--rspec", dest="rspec",
                    default="", action="store", metavar="FILENAME",
                    help="Rspec file to be parsed")
parser.add_argument("-s", "--ssh-config", dest="ssh_config",
                    default="ssh-config", action="store", metavar="FILENAME",
                    help="Output file onto which the SSH configuration is "
                         "written")
args = parser.parse_args()

if not args.rspec:
    print("You must specify an Rspec input file")
    sys.exit(1)

rspec_file = args.rspec
ssh_config_file = args.ssh_config

config_file = open(ssh_config_file, "w")

ssh_config = SSHConfig(SSH_CONFIG_TEMPLATE, HOST_CONFIG_TEMPLATE, IDENTITY_FILE)

xml_file = ET.iterparse(rspec_file)
for _, el in xml_file:
    el.tag = el.tag.split('}', 1)[1]  # strip all namespaces

n = 0
root = xml_file.root
nodes = root.findall(NODE)
n_nodes = len(nodes)
name_template = NODE_NAME.format(len(str(n_nodes)))
for node in nodes:
    component_id = node.get(COMPONENT_ID)
    components = component_id.split("+")
    domain = components[1]
    name = components[3]
    hostname = "{}.{}".format(name, domain)
    ssh_config.add_host(name_template.format(n), hostname)
    n += 1

config_file.write(str(ssh_config))
config_file.close()
