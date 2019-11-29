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


class NotConstantsObj(object):

    def __init__(self):
        self._doublePeering = False
        self._mrai_type = 0
        self._mrai_jitter = 25
        self._PREPATH = "/etc/bird/"

        self._gname = ""
        self._outDir = ""
        self._directories = False
        self._mrai = True
        self._ipNetworks = ""
        self._networks = True
        self._log_mode = "all"

        self._pref_eval = ""

    @property
    def doublePeering(self):
        return self._doublePeering

    @doublePeering.setter
    def doublePeering(self, value):
        self._doublePeering = value

    @doublePeering.deleter
    def doublePeering(self):
        del self._doublePeering

    @property
    def mrai_type(self):
        return self._mrai_type

    @mrai_type.setter
    def mrai_type(self, value):
        self._mrai_type = value

    @mrai_type.deleter
    def mrai_type(self):
        del self._mrai_type

    @property
    def mrai_jitter(self):
        return self._mrai_jitter

    @mrai_jitter.setter
    def mrai_jitter(self, value):
        self._mrai_jitter = value

    @mrai_jitter.deleter
    def mrai_jitter(self):
        del self._mrai_jitter

    @property
    def PREPATH(self):
        return self._PREPATH

    @PREPATH.setter
    def PREPATH(self, value):
        self._PREPATH = value

    @PREPATH.deleter
    def PREPATH(self):
        del self._PREPATH

    @property
    def gname(self):
        return self._gname

    @gname.setter
    def gname(self, value):
        self._gname = value

    @gname.deleter
    def gname(self):
        del self._gname

    @property
    def outDir(self):
        return self._outDir

    @outDir.setter
    def outDir(self, value):
        self._outDir = value

    @outDir.deleter
    def outDir(self):
        del self._outDir

    @property
    def directories(self):
        return self._directories

    @directories.setter
    def directories(self, value):
        self._directories = value

    @directories.deleter
    def directories(self):
        del self._directories

    @property
    def mrai(self):
        return self._mrai

    @mrai.setter
    def mrai(self, value):
        self._mrai = value

    @mrai.deleter
    def mrai(self):
        del self._mrai

    @property
    def ipNetworks(self):
        return self._ipNetworks

    @ipNetworks.setter
    def ipNetworks(self, value):
        self._ipNetworks = value

    @ipNetworks.deleter
    def ipNetworks(self):
        del self._ipNetworks

    @property
    def networks(self):
        return self._networks

    @networks.setter
    def networks(self, value):
        self._networks = value

    @networks.deleter
    def networks(self):
        del self._networks

    @property
    def log_mode(self):
        return self._log_mode

    @log_mode.setter
    def log_mode(self, value):
        self._log_mode = value

    @log_mode.deleter
    def log_mode(self):
        del self._log_mode

    @property
    def pref_eval(self):
        return self._pref_eval

    @pref_eval.setter
    def pref_eval(self, value):
        self._pref_eval = value

    @pref_eval.deleter
    def pref_eval(self):
        del self._pref_eval
