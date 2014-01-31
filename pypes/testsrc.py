STATE_STOP = 0
STATE_PAUSE = 1
STATE_RUNNING = 2

class SrcAtom(object):
    def pull(self):

class BaseSource(object):
    SRCS = ['default']
    SINKS = ['default']

    def __init__(self):
        self._state = STATE_STOP

    def notify(self, packet, sink='default'):
        print("[{}] {}".format('sink', packet))

    def stop(self):
        pass


class TestSrc(BaseSource):
    def __init__(self, n_packets=None, start=0):
        super(TestSrc, self).__init__()

        self.n_packets = n_packets
        self.i = start

    def run(self):
        super(TestSrc, self).run()

        if self.n_packets and self.n_packets >= self.i:
            self.stop()
        
        self.notify(self.i)
        self.i += 1


src = TestSrc(n_packets=3)
while True:
    src.run()

