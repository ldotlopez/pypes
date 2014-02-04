import pickle
from urllib.request import urlopen

from bs4 import BeautifulSoup

from .core import Element, Transformer, Filter, \
    Empty, EOF


class Adder(Transformer):
    def transform(self, x):
        return x + self.kwargs.get('amount', 0)


class SampleSrc(Element):
    #def __init__(self, sample=('foo', 'bar', 'frob')):
    #    super(SampleSrc, self).__init__()
    #    self._sample = list(sample)

    def run(self):
        try:
            sample = self.kwargs.get('sample', [])
            self.put(sample.pop(0))
            return True

        except IndexError:
            self.finish()


class NullSink(Element):
    def run(self):
        try:
            self.get()
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
                self.put(copy, self.output_pattern % n)

            return True

        except Empty:
            return False

        except EOF:
            self.finish()

class HttpSrc(Element):
    def run(self):
        buff = urlopen(self.kwargs.get('url')).read()
        self.put(buff)
        self.finish()


class Soup(Transformer):
    def transform(self, buffer):
        soup = BeautifulSoup(buffer)
        selector = self.kwargs.get('selector')
        if selector:
            return soup.select(selector)
        else:
            return soup


class LambdaFilter(Filter):
    def filter(self, x):
        f = self.kwargs.get('func')
        return f(x)

