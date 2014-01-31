class Empty(Exception): pass
class WriteError(Exception): pass
class ReadError(Exception): pass

class Queue(list):
    def __init__(self):
        super(Queue, self).__init__()
        self._writeable = True
        self._readable = True

    def _put(self, packet):
        if not self._writeable:
            raise WriteError()

        return self.append(packet)

    def _get(self):
        # Queue is closed on the read-end
        if not self._readable:
            raise ReadError()

        try:
            return self.pop(0)
    
        except:
            if self._writeable:
                # There's nothing to read
                raise Empty()
            else:
                # Queue is closed on the write-end
                raise ReadError()

    def _flush(self):
        if not self._readable:
            raise ReadError()

        ret = self.copy()
        self.clear()

        return ret
        

class Pad:
    def __init__(self, q):
        self._q = q

    @property
    def empty(self):
        return len(self) == 0

    @property
    def writeable(self):
        return self._q._writeable

    @property
    def readable(self):
        return self._q._readable

    def _close_write(self):
        self._q._writeable = False

    def _close_read(self):
        self._q._readable = False


class WritePad(Pad):
    def put(self, packet):
        self._q._put(packet)

    def close(self):
        self._close_write()

    #def put(self, packet):
    #    self._data.append(packet)
    #
    #def get(self):
    #    try:
    #        return self._data.pop(0)
    #    except IndexError:
    #        raise Empty()

class ReadPad(Pad):
    def get(self):
        return self._q._get()

    def flush(self):
        return self._q._flush()
