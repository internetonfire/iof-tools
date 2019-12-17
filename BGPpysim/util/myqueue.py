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