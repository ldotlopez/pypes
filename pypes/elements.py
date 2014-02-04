import pickle

from .core import Element, Empty, EOF


class Transformer(Element):
    """Filter implements common functionality for elements with one input and one output
    Derived classes must implement the transform method instead of the run one.
    """
    def run(self):
        try:
            packet = self.get()
            self.put(self.transform(packet))

        except Empty:
            return False

        except EOF:
            self.finish()

    def transform(self, input):
        """Apply whatever is needed and return a value"""
        raise Exception('Not implemented')


class Filter(Element):
    def run(self):
        try:
            packet = self.get()
            if self.filter(packet):
                self.put(packet)
                return True
            else:
                return False

        except Empty:
            return False

        except EOF:
            raise self.finish()

    def filter(self, x):
        """Returns True is x must pass, False elsewhere"""
        raise Exception('Not implemented')


class Adder(Transformer):
    def __init__(self, amount=1):
        self.ammount = amount

    def transform(self, x):
        return x + self.ammount


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

            for n in range(1, self.n_ouputs):
                copy = pickle.loads(pickle.dumps(packet))
                self.put(packet, self.output_pattern % n)

            return True
            
        except Empty:
            return False

        except EOF:
            self.finish()

