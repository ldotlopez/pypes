from functools import wraps


class WriteError(Exception):
    """Write operation can't be performed because write side is closed"""
    pass


class ReadError(Exception):
    """Read operation can't be performed because read side is closed"""
    pass


class Empty(Exception):
    """Read operation can't be performed because there is no data to read"""
    pass


class EOF(Exception):
    """Read operation can't be performed because write side is closed"""
    pass

def check_write(f):
    @wraps(f)
    def wrapped(inst, *args, **kwargs):
        if not inst.writeable:
            raise WriteError()
        return f(inst, *args, **kwargs)

    return wrapped

def check_read(f):
    @wraps(f)
    def wrapped(inst, *args, **kwargs):
        if not inst.readable:
            raise ReadError()

        if len(inst) == 0:
            if inst.writeable:
                raise Empty()
            else:
                raise EOF()

        return f(inst, *args, **kwargs)

    return wrapped


class Queue(list):
    """Queue method must implement at least three methods:
    - put: put a packet into queue
    - get: get packet from queue
    - flush: get all remaining packets from queue
    """
    def __init__(self):
        super(Queue, self).__init__()
        self._can_write = True
        self._can_read = True

    #
    # Decorators for safety checks
    #
    #
    # Readable / Writeable properties (getters and setters)
    #

    @property
    def readable(self):
        """Flag indicating if queue is readable, can be updated to False but not to True"""
        return self._can_read

    @readable.setter
    def readable(self, x):
        if x is True:
            raise ValueError()
        self._can_read = x

    @property
    def writeable(self):
        """Flag indicating if queue is writeable, can be updated to False but not to True"""
        return self._can_write

    @writeable.setter
    def writeable(self, x):
        if x is True:
            raise ValueError()
        self._can_write = x

    #
    # put/get/flush operations
    #

    @check_write
    def put(self, packet):
        """Push packet into queue
        If queue is not writeable WriteError is raised
        """
        return self.append(packet)

    @check_read
    def get(self):
        """Pop a packet from queue
        If there are no packets and queue is writeable Empty is raised
        If there are no packets and queue is not writeable EOF is raised
        If queue is not readable ReadError is raised
        """
        return self.pop(0)
   
    def flush(self):
        """Get all remaining elements from queue
        If queue is not readable ReadError is raised
        If queue is not writeable Empty is raised
        """
        if not self.readable:
            raise ReadError()

        if not self.writeable:
            raise EOF()

        # Not very elegant but...
        ret = list(self)
        while self:
            self.pop()

        return ret
        

class Pad:
    """Pad class is designed to connect Queues and Elements.
    The main porpose of Pad is provide resource and access control to Queue.
    """
    def __init__(self, q):
        self._q = q

    @property
    def empty(self):
        return len(self) == 0

    @property
    def writeable(self):
        return self._q.writeable

    @property
    def readable(self):
        return self._q.readable

    def close_write(self):
        self._q.writeable = False

    def close_read(self):
        self._q.readable = False


class WritePad(Pad):
    def put(self, packet):
        self._q.put(packet)

    def close(self):
        self.close_write()


class ReadPad(Pad):
    def get(self):
        return self._q.get()

    def close(self):
        self.close_read()

    def flush(self):
        return self._q.flush()
