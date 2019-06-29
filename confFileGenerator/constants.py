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
COMMON_FILTERS_TEMPLATE = "templates/common_filters.template"
COMMON_FILTER_FILE_NAME = "commonFilters.conf"

TYPE_KEY = "type"

gname = "small_g.graphml"
outDir = "out/"
src = "baseFiles/"
node_number = 50