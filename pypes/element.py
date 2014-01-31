from .queue import Empty

class Died(Exception): pass

class Element:
    def __init__(self):
        self._alive = True
        self._input, self._output = None, None

    def attach(self, container):
        self._container = container
        self._input, self._output = None, None

    @property
    def alive(self):
        return any([x is not None for x in [self._input, self._output]])

    @property
    def input(self):
        return self._input

    @property
    def output(self):
        return self._output

    @input.setter
    def input(self, queue):
        if self._input:
            raise ValueError()
        self._input = queue

    @output.setter
    def output(self, queue):
        if self._output:
            raise ValueError()
        self._output = queue

    def get(self):
        return self.input.get()

    def put(self, data):
        self.output.put(data)

    def die(self):
        self._input, self._output = None, None
        raise Died()

class SampleSrc(Element):
    def __init__(self, sample=('foo', 'bar', 'frob')):
        super(SampleSrc, self).__init__()
        self._sample = list(sample)

    def run(self):
        try:
            self.put(self._sample.pop(0))
        except IndexError:
            self.output.close()
            self.die()

class NullSink(Element):
    def run(self):
        try:
            x = self.get()

        except Empty:
            return False

        except Died:
            self.input.close()
            self.die()

        return True

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

        except Died:
            self.die()

class Pipeline:
    pass
