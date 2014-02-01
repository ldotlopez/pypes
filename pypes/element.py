from functools import wraps
from .queue import Empty, EOF, ReadError, WriteError

class Done(Exception): pass
class NoInput(Exception): pass
class NoOutput(Exception): pass

def check_alive(f):
    @wraps(f)
    def wrapped(inst, *args, **kwargs):
        if not inst.alive:
            raise Done()
        return f(inst, *args, **kwargs)

    return wrapped

def check_input(f):
    @wraps(f)
    def wrapped(inst, *args, **kwargs):
        if not inst.input:
            raise NoInput()
        return f(inst, *args, **kwargs)

    return wrapped

def check_output(f):
    @wraps(f)
    def wrapped(inst, *args, **kwargs):
        if not inst.output:
            raise NoOutput()
        return f(inst, *args, **kwargs)

    return wrapped


class Element:
    def __init__(self):
        self._alive = True
        self._input, self._output = None, None

    def attach(self, container, input=None, output=None):
        self._container = container
        self._input, self._output = input, output

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

    @check_input
    @check_alive
    def get(self):
        return self.input.get()

    @check_output
    @check_alive
    def put(self, data):
        self.output.put(data)

    def finish(self):
        self._input, self._output = None, None
        self._alive = False
        raise Done()

class SampleSrc(Element):
    def __init__(self, sample=('foo', 'bar', 'frob')):
        super(SampleSrc, self).__init__()
        self._sample = list(sample)

    @check_alive
    def run(self):
        try:
            self.put(self._sample.pop(0))
            return True

        except IndexError:
            self.output.close()
            self.finish()
            

class NullSink(Element):
    def run(self):
        try:
            x = self.get()

        except Empty:
            return False

        except Eof:
            self.input.close()
            self.finish()

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

        except EOF:
            self.finish()

class Pipeline:
    pass
