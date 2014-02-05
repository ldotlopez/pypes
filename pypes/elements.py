import pickle
from urllib.request import urlopen

from bs4 import BeautifulSoup

from .core import Element, Transformer, \
    Empty, EOF


class Adder(Transformer):
    def transform(self, x):
        return x + self.kwargs.get('amount', 0)


class SampleSrc(Element):
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

class Zip(Element):
    def __init__(self, n_inputs=1, input_pattern='zip_%02d'):
        super(Zip, self).__init__(n_inputs=n_inputs, input_pattern=input_pattern)

        self.inputs = [input_pattern % x for x in range(n_inputs)]

    def run(self):
        if not self.inputs:
            self.finish()

        input = self.inputs.pop(0)

        try:
            x = self.get(input)
            self.put(x)
            self.inputs.append(input)
            return True

        except Empty:
            self.inputs.append(input)
            return False

        except EOF:
            return False


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


class Debugger(Element):
    def run(self):
        try:
            import ipdb
            debugger = ipdb
        except ImportError:
            import pdb
            debugger = pdb
        debugger.set_trace()

        try:
            self.put(self.get())
            return True

        except Empty:
            return False

        except EOF:
            self.finish()


class CustomTransformer(Transformer):
    def __init__(self, func=None, *args, **kwargs):
        if not callable(func):
            raise ValueError('func is not a callable')

        self.func = func

    def transform(self, input):
        return self.func(input)
