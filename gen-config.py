#!/usr/bin/env python
import xml.etree.ElementTree as ET
from argparse import ArgumentParser
import sys
from config_templates import SSHConfig, AnsibleConfig

from const import COMPONENT_ID, NODE, SSH_CONFIG_TEMPLATE, \
    HOST_CONFIG_TEMPLATE, IDENTITY_FILE, NODE_NAME, ANSIBLE_CONFIG_TEMPLATE, \
    INVENTORY_CONFIG_TEMPLATE, ANSIBLE_HOST_TEMPLATE

parser = ArgumentParser()
parser.add_argument("-r", "--rspec", dest="rspec",
                    default="", action="store", metavar="FILENAME",
                    help="Rspec file to be parsed")
parser.add_argument("-s", "--ssh-config", dest="ssh_config",
                    default="ssh-config", action="store", metavar="FILENAME",
                    help="Output file onto which the SSH configuration is "
                         "written (default=%(default)s)")
parser.add_argument("-a", "--ansible-config", dest="ansible_config",
                    default="ansible.cfg", action="store", metavar="FILENAME",
                    help="Output file onto which the ansible configuration is "
                         "written (default=%(default)s)")
parser.add_argument("-i", "--inventory", dest="ansible_inventory",
                    default="ansible-hosts", action="store", metavar="FILENAME",
                    help="Output file onto which the ansible inventory is "
                         "written (default=%(default)s)")
parser.add_argument("-k", "--key", dest="identity",
                    default=IDENTITY_FILE, action="store",
                    metavar="FILENAME",
                    help="Private key or certificate used for the "
                         "authentication (default=%(default)s)")

args = parser.parse_args()

if not args.rspec:
    print("You must specify an Rspec input file")
    sys.exit(1)

rspec_file = args.rspec
ssh_config_file = args.ssh_config
ansible_config_file = args.ansible_config
ansible_inventory_file = args.ansible_inventory
identity_file = args.identity

config_file = open(ssh_config_file, "w")
ansible_file = open(ansible_config_file, "w")
inventory_file = open(ansible_inventory_file, "w")

ssh_config = SSHConfig(SSH_CONFIG_TEMPLATE, HOST_CONFIG_TEMPLATE, identity_file)
ansible_config = AnsibleConfig(ANSIBLE_CONFIG_TEMPLATE,
                               INVENTORY_CONFIG_TEMPLATE,
                               ANSIBLE_HOST_TEMPLATE, identity_file,
                               ansible_inventory_file, ssh_config_file)

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
    friendly_name = name_template.format(n)
    ssh_config.add_host(friendly_name, hostname)
    ansible_config.add_host(friendly_name)
    n += 1

config_file.write(str(ssh_config))
ansible_file.write(ansible_config.get_ansible_config())
inventory_file.write(ansible_config.get_ansible_inventory())

config_file.close()
ansible_file.close()
inventory_file.close()
