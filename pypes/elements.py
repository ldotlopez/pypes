import pickle

from .core import Element, Empty, EOF

class SampleSrc(Element):
    def __init__(self, sample=('foo', 'bar', 'frob')):
        super(SampleSrc, self).__init__()
        self._sample = list(sample)

    def run(self):
        try:
            self.put(self._sample.pop(0))
            return True

        except IndexError:
            self.finish()


class Adder(Element):
    def __init__(self, ammount=1):
        self.ammount = ammount

    def run(self):
        try:
            self.put(self.get() + self.ammount)
            return True

        except Empty:
            return False

        except EOF:
            self.finish()


class NullSink(Element):
    def run(self):
        try:
            x = self.get()
            return True

        except Empty:
            return False

        except EOF:
            self.finish()


class StoreSink(Element):
    def __init__(self):
        super(StoreSink, self).__init__()
        self.store = []

    def run(self):
        try:
            self.store.append(self.get())
            return True

        except Empty:
            return False

        except EOF:
            self.finish()


class Tee(Element):
    def __init__(self, n_ouputs, output_pattern='tee_%02d'):
        self.n_ouputs = n_ouputs
        self.output_pattern = output_pattern

    def run(self):
        try:
            packet = self.get()
            self.put(packet, self.output_pattern % 0)

            for n in range(0, self.n_ouputs - 1):
                copy = pickle.loads(pickle.dumps(packet))
                self.put(packet, self.output_pattern % n)

            return True
            
        except Empty:
            return False

        except EOF:
            self.finish()

