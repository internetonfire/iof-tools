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
class MyQueue(object):

    def __init__(self):
        self.q = []

    def push(self, item):
        self.q.append(item)

    def enqueue(self, item):
        self.q.append(item)

    def pop(self):
        return self.q.pop(0)

    def dequeue(self):
        return self.q.pop(0)

    def get(self, item):
        return self.q[0]

    def isEmpty(self):
        return not self.q