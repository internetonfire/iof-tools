#!/usr/bin/python
#==============================================================================
# Copyright (C) 2019-2024 Mattia Milani, Leonardo Maccari, Luca Baldesi, Lorenzo Ghiro, Michele Segata, Marco Nesler 
#
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
#==============================================================================

class EventLog(object):
    """
    Class EventLog, used to log events in a given format
    """

    def __init__(self, time, evType, evFrom, prefix, as_path, binPref='ND'):
        """
        Initialization on an eventLog element
        :param time: when the event happen
        :param evType: type of the event
        :param evFrom: who trigger the event
        :param prefix: Prefix that trigger the event
        :param as_path: Path in the packet of the event
        :param binPref: given fabrikant path
        """
        self.time = time
        self.evType = evType
        self.evFrom = evFrom
        self.prefix = prefix
        self.as_path = as_path
        self.binPref = binPref

    def to_dict(self):
        return self.__dict__
