import pickle
from urllib.request import urlopen

from ldotcommons.utils import get_debugger

from .core import Element, Filter, Transformer, \
    Empty, EOF


class Adder(Transformer):
    def transform(self, x):
        return x + self.kwargs.get('amount', 0)


class CustomTransformer(Transformer):
    def __init__(self, func=None, *args, **kwargs):
        super(CustomTransformer, self).__init__(*args, **kwargs)

        if not callable(func):
            raise ValueError('func is not a callable')

        self.func = func

    def transform(self, input):
        return self.func(input)


class CustomFilter(Filter):
    def __init__(self, func=None, *args, **kwargs):
        super(CustomTransformer, self).__init__(*args, **kwargs)

        if not callable(func):
            raise ValueError('func is not a callable')

        self.func = func

    def filter(self, input):
        return self.func(input)


class Debugger(Element):
    def run(self):
        get_debugger().set_trace()

        try:
            self.put(self.get())
            return True

        except Empty:
            return False

        except EOF:
            self.finish()


class DictFixer(Transformer):
    """
    Applies changes to dicts
    Parameters:
    - override: Boolean to control if values should be overriden (forced)
    - values: dict with new values
    """
    def transform(self, packet):
        if not isinstance(packet, dict):
            raise ValueError('Packet is not a dict object')

        override = self.kwargs.get('override', False)
        values = self.kwargs.get('values', {})

        if not override:
            values = {key: value for (key, value) in values.items() if key not in packet}

        packet.update(values)
        return packet


class DictFilter(Transformer):
    def transform(self, packet):
        if not isinstance(packet, dict):
            raise ValueError('Packet is not a dict object')

        keys = self.kwargs.get('keys', None)
        if keys is None:
            return packet

        return {key: value for (key, value) in packet.items() if key in keys}


class FetcherProcessor(Transformer):
    def transform(self, url):
        return self.kwargs.get('fetcher').fetch(url)


class GeneratorSrc(Element):
    def __init__(self, generator=None, iterations=-1, *args, **kwargs):
        super(GeneratorSrc, self).__init__(*args, **kwargs)

        self.g = generator
        self.i = 0
        self.n = iterations

    def run(self):
        if self.n >= 0 and self.i >= self.n:
            self.finish()

        try:
            packet = next(self.g)
            self.put(packet)
            self.i += 1

        except StopIteration:
            self.finish()


class Head(Filter):
    def __init__(self, n=-1, *args, **kwargs):
        super(Head, self).__init__(*args, **kwargs)
        self.n = n
        self.i = 0

    def filter(self, packet):
        r = self.n == -1 or self.i < self.n
        self.i += 1

        return r


class HttpSrc(Element):
    def run(self):
        buff = urlopen(self.kwargs.get('url')).read()
        self.put(buff)
        self.finish()


class NullSrc(Element):
    def run(self):
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


class Packer(Element):
    def __init__(self, *args, **kwargs):
        super(Packer, self).__init__(self, *args, **kwargs)
        self._packets = []

    def run(self):
        try:
            self._packets.append(self.get())
            return True

        except Empty:
            return False

        except EOF:
            self.put(self._packets)
            self.finish()


class PickleSrc(Element):
    def __init__(self, filename=None):
        fh = open(filename)
        self.packets = pickle.load(fh)
        fh.close()

    def run(self):
        try:
            packet = self.packets.pop()
            self.put(packet)

        except IndexError:
            self.finish()


class PickleSink(Element):
    def __init__(self, **kwargs):
        filename = kwargs.pop('filename', None)

        super(PickleSink, self).__init__(**kwargs)
        self.filename = filename
        self.packets = []

    def run(self):
        try:
            self.packets.append(self.get())
            return True

        except Empty:
            return False

        except EOF:
            fh = open(self.filename, 'wb+')
            pickle.dump(self.packets, fh)
            fh.close()

            self.finish()


class SampleSrc(Element):
    def run(self):
        try:
            sample = self.kwargs.get('sample', [])
            self.put(sample.pop(0))
            return True

        except IndexError:
            self.finish()


class StoreSink(Element):
    def __init__(self, *args, **kwargs):
        super(StoreSink, self).__init__(*args, **kwargs)
        self.packets = []

    def run(self):
        try:
            self.packets.append(self.get())
            return True

        except Empty:
            return False

        except EOF:
            self.finish()


class Tee(Element):
    def __init__(self, *args, n_outputs=1, output_pattern='tee_%02d', **kwargs):
        super(Tee, self).__init__(args, **kwargs)
        self.n_outputs = n_outputs
        self.output_pattern = output_pattern

    def run(self):
        try:
            packet = self.get()
            self.put(packet, self.output_pattern % 0)

            for n in range(1, self.n_outputs):
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
