#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright (C) 2019  Mattia Milani <mattia.milani@studenti.unitn.it>

HOLD_TIMER = "15"
CONNECT_RETRY_TIMER = "5"
CONNECT_DELAY_TIMER = "10"
STARTUP_HOLD_TIMER = "10"
LOCAL_PREF = "99"
LOG_MODE = "all"
DBG_MODE = "all"
DBG_COMMANDS_MODE = "2"
# TODO not constant
PREPATH = "/etc/bird/"
KERNEL_CONF_PATH = "kernel.conf"
DIRECT_CONF_PATH = "direct.conf"
DEVICE_CONF_PATH = "device.conf"
FILTER_CONF_PATH = "commonFilters.conf"

BGP_SESSION_TEMPLATE_PATH = "templates/bgpSession_template.template"
BGP_SESSION_EXPORTER_TEMPLATE_PATH = "templates/bgpSessionExporter_template.template"
BGP_SESSION_STATIC_EXPORTER_TEMPLATE_PATH_UPLINKS = "templates/bgpSession_static_route_template_uplinks.template"
BGP_SESSION_STATIC_EXPORTER_TEMPLATE_PATH_PEERS = "templates/bgpSession_static_route_template_peers.template"
BGP_SESSION_STATIC_EXPORTER_TEMPLATE_PATH_CLIENTS = "templates/bgpSession_static_route_template_clients.template"
BIRD_TEMPLATE_PATH = "templates/bird_template.template"
MRAI_TEMPLATE_FILE = "templates/mrai.template"
NETWORK_TEMPLATE_PATH = "network_config.template"

TYPE_KEY = "type"

ARGS = ['graph=', 'out=', 'nnodes=', 'directories', 'help', 'h', 'nomrai', 'mraitype=', 'prepath=', 'ipnetworksgraph=',
        'noautomaticnetworks', 'preferences=', 'doublepeering']

gname = "small_g.graphml"
outDir = "out/"
src = "baseFiles/"
node_number = 20
# TODO not constant
mrai_type = 0
# TODO not constant
doublepeering = False

HELP_MESSAGE = """
Mandatory args are: 
    --graph [file name]: name of the graphml (only graphml files are accepted) file that will be used to generate the conf files, this file needs to be correctly formatted and created. Only nodes of type 'C' generates routes. If this does not exists yet it will be created with a predefined number of nodes (20).
    --out [folder name]: folder where the conf files will be saved

Not mandatory args:
    --nnodes [number]: redefine the default number of nodes used to create the file, if the file already exists this parameter will be ignored
    --directories: this arg does not require parameters, if present the output will be formatted to folders, for each bird node
    --help, -h: show this help
    --nomrai: this option will override the mrai in the graphml file and preclude mrai commands to be in the conf file (To make the conf files compatibles with old bird daemons)
    --mraitype: define the type of mrai that will be used in the conf files, default is 0
    --prepath: path used in front of all files (use the path where the conf files will be saved), default is "/etc/bird/"
    --ipnetworksgraph: defines the name of the attribute in the graphml file that represents the network address list that will be shared by anode, it needs to be a node attribute and since it's not possible to define a list inside a graphml attribute, network addresses should respect the following rule `[addr]/[netmask 8 to 24],[addr2]/[netmask], ecc`, **no checks are performed between networks**
    --noautomaticnetworks: if a C node has 0 networks defined with ipnetworksgraph or if ipnetworksgraph is not defined, an automatic network will be assigned to the node, with this param the automatic network will not be assigned, so a C could share 0 networks
    --prefpreferences [attr_name]: name of the attribute that defines in the graphml file the preferences, if some edges does not have this attribute will be used the default value of 1, you can set a double value of pref with "pref1,pref2" for and edge A->B, the first value will be used for the relation A->B and the second one for the relation B->A, if only one value is specified "pref", it will be used for both relations
    --doublepeering: if used this param will suppose to use a graphml file that have two edges for a peering relation, otherwise is supposed that the graphml have just one edge for the peering relation, and this edge will be used to create both relation files

Example command:

`python3 confFileGen.py --graph graph.graphml --out out/ --nnodes 10 --directories`

This command generate the file graph.graphml if it does not exists and will be used only 10 nodes (instead of 20, default for new files).
Will be used the 'out' directory to save the files, and thanks to `--directories` all files will be moved to the corresponding directory. 
with this command will also be inserted the commands for mrai, to avoid this is possible to use the following command:

`python3 confFileGen.py --graph graph.graphml --out out/ --nnodes 10 --directories --nomrai`

Is possible to set the interface addresses for each link, with the attributes:
    ip_eth_n1
    ip_eth_n1
The two ip needs to be part of the same `/30` network, **there is no check between couple of interfaces that networks addresses are not already in use**  
"""