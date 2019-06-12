#!/usr/bin/env python
import xml.etree.ElementTree as ET

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from subprocess import check_output
from argparse import ArgumentParser
import sys

from const import AVAILABLE, COMPONENT_ID, COMPONENT_NAME, FOOTER_TEMPLATE, \
    HARDWARE_TYPE, HEADER_TEMPLATE, LOCATION, NAME, NODE, NODE_TEMPLATE, NOW, \
    TRUE, X, Y, Z


def matches(name, filters, nodes):
    if len(nodes) > 0:
        return name in nodes
    if len(filters) == 0:
        return True
    for f in filters:
        if name.startswith(f):
            return True
    return False


def matches_hardware(hardware_filter, hardware_types):
    if len(hardware_filter) == 0:
        return True
    for f in hardware_filter:
        for h in hardware_types:
            if h.startswith(f):
                return True
    return False


def fetch_nodes(testbed, n, use_hardware, filters, nodes, hardware_types,
                dump_file, df):
    omni = ["./omni", "-V3", "listresources", "-a", testbed, "--error",
            "--tostdout"]

    xml = check_output(omni)

    # parse the xml file removing the namespaces from tag names
    xml_file = StringIO(xml.decode('utf-8'))
    it = ET.iterparse(xml_file)
    for _, el in it:
        el.tag = el.tag.split('}', 1)[1]  # strip all namespaces
    e = it.root

    t = __import__('%stemplates' % testbed, globals(), locals(),
                   [NODE_TEMPLATE, HEADER_TEMPLATE, FOOTER_TEMPLATE])
    h = 40
    w = 120
    xs = 100
    ys = 100

    xml = ""

    for node in e.findall(NODE):
        name = node.get(COMPONENT_NAME)
        available = node.find(AVAILABLE).get(NOW).lower() == TRUE
        has_position = X in node.find(LOCATION).attrib
        component_id = node.get(COMPONENT_ID)
        if has_position:
            x = float(node.find(LOCATION).get(X))
            y = float(node.find(LOCATION).get(Y))
            z = float(node.find(LOCATION).get(Z))
        else:
            x = 0
            y = 0
            z = 0
        row = (n - 1) / 8
        col = (n - 1) % 8
        good_node = False
        if use_hardware:
            hardware_type_nodes = node.findall(HARDWARE_TYPE)
            hardware_types = [ht.get(NAME) for ht in hardware_type_nodes]
            if available and matches_hardware(hardware, hardware_types):
                good_node = True
        else:
            if available and matches(name, filters, nodes):
                good_node = True

        if good_node:
            domain = component_id.split("+")[1]
            hostname = "{}.{}".format(name, domain)
            xml += t.node_template % \
                   (name, component_id, xs + col * w, ys + row * h)
            if dump_file != "":
                df.write("%s\n" % name)
            n += 1
    return n, xml


parser = ArgumentParser()
parser.add_argument("-t", "--testbed", dest="testbed",
                    default="wall1", action="store", metavar="TESTBED",
                    help="Comma separated list of testbeds to use [default: "
                         "%(default)s]")
parser.add_argument("-f", "--filter", dest="filter",
                    default="", action="store", metavar="List of filters",
                    help="Comma separated list of node prefixes [default: %("
                         "default)s]")
parser.add_argument("-w", "--hardware", dest="hardware",
                    default="", action="store", metavar="List of hardware",
                    help="Comma separated list of hardware types [default: %("
                         "default)s]")
parser.add_argument("-n", "--nodes", dest="nodes",
                    default="", action="store", metavar="List of nodes",
                    help="Comma separated list of nodes [default: %("
                         "default)s] This argument has precedence over "
                         "--filter")
parser.add_argument("-d", "--dump", dest="dump",
                    default="", action="store", metavar="FILENAME",
                    help="Output file where to store the list of available "
                         "nodes. If not specified, no file will be written")
args = parser.parse_args()

if args.filter and args.hardware:
    print("Cannot use the --filter and the --hardware options together")
    sys.exit(1)

testbeds = args.testbed.split(",")
use_hardware = False
if args.filter:
    filters = args.filter.split(",")
else:
    filters = []

if args.nodes:
    nodes = args.nodes.split(",")
else:
    nodes = []

if args.hardware:
    use_hardware = True
    hardware = args.hardware.split(",")
else:
    hardware = []

dump_file = args.dump

t = __import__('%stemplates' % testbeds[0], globals(), locals(),
               [NODE_TEMPLATE, HEADER_TEMPLATE, FOOTER_TEMPLATE])

df = None
if dump_file != "":
    df = open(dump_file, "w")

print(t.header_template)

n = 0
for testbed in testbeds:
    n, xml = fetch_nodes(testbed, n, use_hardware, filters, nodes, hardware,
                         dump_file, df)
    print(xml)

print(t.footer_template)

if dump_file != "":
    df.close()
