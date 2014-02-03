import logging
import os
import sys

_loggers = {}

LOGGING_FORMAT = "[%(levelname)s] %(name)s: %(message)s"

class EncodedStreamHandler(logging.StreamHandler):
    def __init__(self, *args, encoding='utf-8', **kwargs):
        super(EncodedStreamHandler, self).__init__(*args, **kwargs)
        self.encoding = encoding
        self.terminator = self.terminator.encode(self.encoding)

    def emit(self, record):
        try:
            msg = self.format(record).encode(self.encoding)
            stream = self.stream
            stream.buffer.write(msg)
            stream.buffer.write(self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)


def get_logger(key=os.path.basename(sys.argv[0])):
    global _loggers

    if not key in _loggers:
        _loggers[key] = logging.getLogger(key)
        _loggers[key].setLevel(logging.DEBUG)

        handler = EncodedStreamHandler()
        handler.setFormatter(logging.Formatter(LOGGING_FORMAT))
        _loggers[key].addHandler(handler)

    return _loggers[key]
