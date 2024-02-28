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

import heapq
import random


class EventScheduler:
    """
    Class used to schedule events in an event discrete space
    """

    def __init__(self):
        self.queue = []
        self.time = 0
        self.last = 0
        self._step = 0
        self.counter = 0

    def jitter(self, positive=True):
        """
        Function to introduce a jitter in the a jitter in the event
        :param positive: if true it will introduce the jitter
        :return:
        """
        if positive:
            return random.uniform(0, 0.1)
        else:
            return [-1, 1][random.randrange(2)] * random.uniform(0, 0.866)

    def schedule_event(self, interval, e):
        """
        Function to schedule an event after a certain interval
        :param interval: After how much the event will be scheduled
        :param e: event to schedule
        """
        t = self.time + interval
        if t > self.last:
            self.last = t
        heapq.heappush(self.queue, (t, e))

    def pop_event(self):
        """
        Function to take the next event in the queue
        :return: the next event in the queue
        """
        e = heapq.heappop(self.queue)
        self._step = e[0] - self.time
        self.time = e[0]
        self.counter += 1
        return e[1]

    def elapsed_time(self):
        """
        Function to know how much time is elapsed
        :return: the actual time
        """
        return self.time

    def last_event_time(self):
        """
        Function to know when the last event will happen
        :return: the time of the last event
        """
        return self.last

    def step(self):
        """
        Function to get the step time
        :return: the step time
        """
        return self._step

    def processed_events(self):
        """
        Function to get the total amount of events processed
        :return: number of events
        """
        return self.counter
