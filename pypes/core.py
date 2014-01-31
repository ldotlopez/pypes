class Empty(Exception): pass
class Dead(Exception): pass

class Pad(object):

    """Generic pad object"""
    def __init__(self, element):
        self._element = element
        self.data = []
        self._alive= True

    @property
    def element(self):
        return self._element

    @property
    def is_alive(self):
        return self._alive

    def die(self):
        self._alive = False

    def put(self, *packets):
        if not self.is_alive:
            raise Dead()

        self.data += packets

    def get(self):
        while True:
            try:
                x = self.data.pop(0)
            except IndexError:
                break

            yield x

        if self.is_alive:
            raise StopIteration()
        else:
            raise Dead()

class InputPad(Pad):
    """Read-only pad object"""
    def __getattribute__(self, name):
        if name == 'put':
            raise AttributeError(name)
        return super(InputPad, self).__getattribute__(name)


class OutputPad(Pad):
    """Write-only pad object"""
    def __getattribute__(self, name):
        if name in ('get', 'get_all'):
            raise AttributeError(name)
        return super(OutputPad, self).__getattribute__(name)


class BaseElement(object):
    inputs = ['default']
    outputs = ['default']

    def __init__(self):
        input_names = self.__class__.inputs if hasattr(self.__class__, 'inputs') else ('default', )
        output_names = self.__class__.outputs if hasattr(self.__class__, 'outputs') else ('default', )

        self.inputs = { name: InputPad(self) for name in input_names }
        self.outputs = { name: OutputPad(self) for name in output_names }

    #
    # Put/get/flush
    #

    def put(self, *packets, **kwargs):
        name = kwargs.get('name', 'default')
        self.outputs[name].put(*packets)

    def get(self, name='default'):
        for x in self.inputs[name].get():
            yield x

    def run(self):
        raise StopIteration()

    def get_input(self, name='default'):
        return self.inputs[name]

    def get_output(self, name='default'):
        return self.outputs[name]


class DigitSrc(BaseElement):
    name = 'Digit generator'
    inputs = []

    def __init__(self, max=10):
        super(DigitSrc, self).__init__()
        self.i = 0
        self.max = max

    def run(self):
        if self.i >= self.max:
            self.close()
            raise StopIteration()

        self.put(self.i)
        self.i += 1

class ConsoleSink(BaseElement):
    name = 'Console printer'
    outputs = []

    def run(self):
        while True:
            try:
                packet = self.get()
                print("{}".format(packet))

            except Empty:
                return

            except Close:
                raise StopIteration()


class Pipeline(object):
    def __init__(self):
        self._elements = set()
        self._connections = {}
        self._backpath = {}

    def connect(self, src, sink, srcpad='default', sinkpad='default'):
        self._elements.add(src)
        self._elements.add(sink)

        # +-----+-++     ++-+------+
        # | src |O|| --> ||I| sink |
        # +-----+-++     ++-+------+
        #        |          `- sinkpad
        #        `- srcpad

        srcpad = src.get_output(srcpad)
        sinkpad = sink.get_input(sinkpad)

        self._connections[srcpad] = sinkpad
        self._backpath[sinkpad] = srcpad

    def run(self):
        closed = []

        for element in self._elements:
            try:
                element.run()
            except Close:
                closed.append(element)
 
            for output in element.outputs_with_data:
                self._connections[output].put(output.flush())


class TestSrc(BaseElement):
    name = 'test source element'
    srcs = ['default']
    sinks = ['default']

    def __init__(self, blocks):
        super(TestSrc, self).__init__()
        self._blocks = blocks 

    def run(self):
        try:
            block = self._blocks.pop(0)
            self.put(*block)

        except IndexError:
            raise StopIteration()

