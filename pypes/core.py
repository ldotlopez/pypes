from functools import wraps
from .logging import get_logger

class WriteError(Exception): pass
class ReadError(Exception): pass
class UnknowElement(Exception): pass
class Finish(Exception): pass
class Empty(Exception): pass
class EOF(Exception): pass

_logger = get_logger()

class Element:
    def attach(self, container):
        self._container = container

    def __str__(self):
        return "{}-{}".format(self.__class__.__name__, id(self))

    def get(self, input='default'):
        packet = self._container.get(self, input)
        _logger.debug("GET [{}] <- {}::{}".format(self, input, packet))
        return packet

    def put(self, packet, output='default'):
        _logger.debug("PUT [{}] -> {}::{}".format(self, output, packet))
        self._container.put(self, packet, output)

    def finish(self):
        _logger.debug("FINISH {}".format(self))
        raise Finish()


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


class Pipeline:
    def __init__(self):
        self._elements = set()

        # Dict of queues using src element has key
        self._queues = {}

        # Dict of queues using sink element has key
        self._rev_queues = {} 

        # Relations between srcs and sinks
        self._rels = {}

        # Relations between sinks and srcs
        self._rev_rels = {}

    def connect(self, src, sink, src_output='default', sink_input='default'):
        # Insert elements
        self._elements.add(src)
        src.attach(self)

        self._elements.add(sink)
        sink.attach(self)

        q = []
        self._queues[src] = q
        self._rev_queues[sink] = q

        self._rels[src] = sink
        self._rev_rels[sink] = src

        _logger.debug("CONNECT [{}] -> [{}]".format(str(src), str(sink)))

    def is_src(self, src):
        return src in self._queues

    def is_sink(self, sink):
        return sink in self._rev_queues

    def src_for(self, sink):
        try:
            return self._rev_rels[sink]
        except KeyError:
            raise UnknowElement()

    def sink_for(self, src):
        try:
            return self._rels.get[src]
        except KeyError:
            raise UnknowElement()

    def write_queue(self, src):
        if not self.is_src(src):
            raise WriteError()

        return self._queues[src]

    def read_queue(self, sink):
        if not self.is_sink(sink):
            raise ReadError()

        # src_for_sink = self.src_for(sink)
        return self._rev_queues[sink]


    def put(self, element, packet, output='default'):
        """Puts a packet from elment into the pipeline flow
        Raises UnknowElement if element is not in pipeline
        Raises WriteError if element has no writeable queue
        """

        if not element in self._elements:
            raise UnknowElement()

        self.write_queue(element).append(packet)


    def get(self, sink, input='default'):
        """Gets a packet for sink from the pipeline flow
        Raises Empty if there is not data to read
        Raises UnknowElement if sink is not in pipeline
        Raises ReadError if sink has no readable queue
        Raises EOF if there is no more data and not write sink on the other side
        """
        
        if not sink in self._elements:
            raise UnknowElement()

        if not self.is_sink(sink):
            raise ReadError()

        try:
            return self.read_queue(sink).pop(0)
        except IndexError:
            # Check if queue has reached EOF
            src = self.src_for(sink)
            if src not in self._queues:
                raise EOF()
            else:
                raise Empty()

    def disconnect(self, element):
        if self.is_src(element):
            del self._rels[element]
            del self._queues[element]

        if self.is_sink(element):
            del self._rev_queues[element]
            del self._rev_rels[element]


        self._elements.remove(element)

    def run(self):
        finished = []

        for element in self._elements:
            try:
                element.run()
            except Finish:
                finished.append(element)

        for element in finished:
            self.disconnect(element)

        return len(self._elements) > 0

