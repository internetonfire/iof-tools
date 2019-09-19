import heapq
import random

class EventScheduler:
        def __init__(self):
                self.queue = []
                self.time = 0
                self.last = 0
                self._step = 0
                self.counter = 0

        def jitter(self, positive=True):
            if positive:
                return random.uniform(0, 0.0001)
            else:
                return [-1, 1][random.randrange(2)]*random.uniform(0, 0.866)

        def schedule_event(self, interval, e):
                t = self.time + interval
                if t > self.last:
                    self.last = t
                heapq.heappush(self.queue, (t, e))

        def pop_event(self):
                e = heapq.heappop(self.queue)
                self._step = e[0] - self.time
                self.time = e[0]
                self.counter += 1
                return e[1]

        def elapsed_time(self):
                return self.time

        def last_event_time(self):
                return self.last

        def step(self):
            return self._step

        def processed_events(self):
            return self.counter