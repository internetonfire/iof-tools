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
KERNEL_CONF_PATH = "/etc/bird/kernel.conf"
DIRECT_CONF_PATH = "/etc/bird/direct.conf"
DEVICE_CONF_PATH = "/etc/bird/device.conf"
FILTER_CONF_PATH = "/etc/bird/commonFilters.conf"

BGP_SESSION_TEMPLATE_PATH = "templates/bgpSession_template.template"
BGP_SESSION_EXPORTER_TEMPLATE_PATH = "templates/bgpSessionExporter_template.template"
BGP_SESSION_STATIC_EXPORTER_TEMPLATE_PATH_UPLINKS = "templates/bgpSession_static_route_template_uplinks.template"
BGP_SESSION_STATIC_EXPORTER_TEMPLATE_PATH_PEERS = "templates/bgpSession_static_route_template_peers.template"
BGP_SESSION_STATIC_EXPORTER_TEMPLATE_PATH_CLIENTS = "templates/bgpSession_static_route_template_clients.template"
BIRD_TEMPLATE_PATH = "templates/bird_template.template"
MRAI_TEMPLATE_FILE = "templates/mrai.template"
NETWORK_TEMPLATE_PATH = "network_config.template"

TYPE_KEY = "type"

gname = "small_g.graphml"
outDir = "out/"
src = "baseFiles/"
node_number = 20
mrai_type = 0

HELP_MESSAGE = """
Conf file generator for bird written by Mattia Milani, mattia.milani@studenti.unitn.it
Mandatory args are: 
    --graph [file name] -> name of the graphml (only graphml files are accepted) file that will be used to generate the conf files, this file needs to be correctly formatted and created.
                            Is possible to use the 'internet_as_graph()' function that can be found at: 'https://github.com/leonardomaccari/networkx/blob/degree_bug/networkx/generators/tests/test_internet_AS_graph.py'
                            Only nodes of type 'C' generates routes
                            type of edges:
                                transit: the first node of this edge pay the second one to transit through it, so the relation is customer <-> servicer
                                peer: the two nodes share a peer relation
                            the sharing policy is based on witch node send the information:
                                customer: shared with everyone
                                servicer: shared with customers
                                peer: shared with customers
                            If this does not exists yet it will be created with a predefined number of nodes (20)
    --out [folder name] -> folder where the conf files will be saved
Not mandatory args:
    --nnodes [number]-> redefine the default number of nodes used to create the file, if the file already exists this parameter will be ignored
    --directories -> this args does not require parameters, if present the output will be formatted to folders for each bird node
    '--help', '-h' -> show this help
"""