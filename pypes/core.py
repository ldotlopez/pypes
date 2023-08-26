from ldotcommons.logging import get_logger

_logger = get_logger()


class WriteError(Exception):
    pass


class ReadError(Exception):
    pass


class UnknowElement(Exception):
    pass


class Finish(Exception):
    pass


class Empty(Exception):
    pass


class EOF(Exception):
    pass


class Element:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self._name = self.kwargs.get("name", self.__class__.__name__)

    def __str__(self):
        return f"{self.__class__.__name__}-{id(self)}"

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, v):
        raise TypeError("name property is read-only")

    def attach(self, container):
        self._container = container

    def get(self, input="default"):
        packet = self._container.get_packet(self, input)
        return packet

    def put(self, packet, output="default"):
        self._container.put_packet(self, packet, output)

    def finish(self):
        # _logger.debug("FINISH {}".format(self))
        raise Finish()


class Pipeline:
    def __init__(self):
        self._elements = set()
        self._table = {}

        # Dict of queues using src element has key
        self._queues = {}

        # Dict of queues using sink element has key
        self._rev_queues = {}

        # Relations between srcs and sinks
        self._rels = {}

        # Relations between sinks and srcs
        self._rev_rels = {}

    def _insert(self, element):
        self._elements.add(element)
        element.attach(self)

        i = 0
        while True:
            key = element.name
            if i > 0:
                key += f"-{i}"
            if key not in self._table:
                break
            i += 1

        self._table[key] = element

    def connect(self, src, sink, src_output="default", sink_input="default"):
        for e, etype in [(src, "src"), (sink, "sink")]:
            if not isinstance(e, Element):
                raise Exception(f"{etype} '{e}' is not a pypes element")

        # Insert elements
        self._insert(src)
        self._insert(sink)

        q = []
        self._queues[(src, src_output)] = q
        self._rev_queues[(sink, sink_input)] = q

        self._rels[(src, src_output)] = (sink, sink_input)
        self._rev_rels[(sink, sink_input)] = (src, src_output)

        # _logger.debug("CONNECT [{}::{}] -> [{}::{}]".format(src, src_output, sink, sink_input))

        return self

    def connect_many(self, *args):
        for idx in range(0, len(args) - 1):
            self.connect(args[idx], args[idx + 1])

        return self

    def get(self, *args, **kwargs):
        return self._table.get(*args, **kwargs)

    def get_write_queue(self, element, name="default"):
        try:
            return self._queues[(element, name)]
        except KeyError:
            pass

        raise WriteError(f"Queue '{name}' not defined for '{element}'")

    def get_read_queue(self, element, name="default"):
        try:
            return self._rev_queues[(element, name)]
        except KeyError:
            pass

        raise ReadError(f"Queue '{name}' not defined for '{element}'")

    def is_src(self, src, output="default"):
        return (src, output) in self._queues

    def is_sink(self, sink, input="default"):
        return (sink, input) in self._rev_queues

    def src_for(self, sink, input="default"):
        try:
            return self._rev_rels[(sink, input)]
        except KeyError:
            pass

        raise UnknowElement(
            "Combination of '{}' and queue '{}' has no reverse matching".format(
                sink, input
            )
        )

    def put_packet(self, src, packet, output="default"):
        """Puts a packet from elment into the pipeline flow
        Raises UnknowElement if element is not in pipeline
        Raises WriteError if element has no writeable queue
        """
        if not src in self._elements:
            raise UnknowElement(
                f"Combination of '{src}' and queue '{output}' has no matching"
            )

        self.get_write_queue(src, output).append(packet)

    def get_packet(self, sink, input="default"):
        """Gets a packet for the sink:input pair from the pipeline flow
        Raises Empty if there is not data to read
        Raises UnknowElement if sink is not in pipeline
        Raises ReadError if sink has no readable queue
        Raises EOF if there is no more data and there is not source on the other side
        """

        if not sink in self._elements:
            raise UnknowElement()

        if not self.is_sink(sink, input):
            raise ReadError()

        try:
            packet = self.get_read_queue(sink, input).pop(0)
            # _logger.debug("GET [{}] <- {}::{}".format(sink, input, packet))
            return packet

        except IndexError:
            pass

        # Check if queue has reached EOF
        (src, output) = self.src_for(sink, input)
        if (src, output) not in self._queues:
            raise EOF()
        else:
            raise Empty()

    def disconnect(self, element):
        self._queues = {k: v for (k, v) in self._queues.items() if k[0] != element}
        self._rev_queues = {
            k: v for (k, v) in self._rev_queues.items() if k[0] != element
        }

        self._rels = {k: v for (k, v) in self._rels.items() if k[0] != element}
        self._rev_rels = {k: v for (k, v) in self._rev_rels.items() if k[0] != element}

        # Elements are removed from _elements list but not from _table because they must be available even after execution
        self._elements.remove(element)
        # self._table = {k: v for (k, v) in self._table.items() if v != element}

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

    def execute(self):
        while self.run():
            pass


class Transformer(Element):
    """Transformer implements common functionality for elements with one input and one output
    Derived classes must implement the 'transform' method instead of the 'run' one.
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
        """Apply whatever is needed and return the transformed value"""
        raise Exception("Not implemented")


class Filter(Element):
    """
    Filter allows to write elements with similar functionality to the builtins.filter method
    Derived classes must implement the 'filter' function with similar behaviour to  builtins.filter
    """

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
        """Returns True if x must pass, False elsewhere"""
        raise Exception("Not implemented")
