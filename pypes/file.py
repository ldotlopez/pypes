from . import EOF, Element, Empty


class FileSrc(Element):
    allowed_modes = ("r", "rb")

    def __init__(self, path=None, mode="rb", bytes=-1):
        if not path:
            raise ValueError("path not specified")

        if mode not in FileSrc.allowed_modes:
            raise ValueError(f"mode must in one of {FileSrc.allowed_modes}")

        if bytes <= 0 and bytes != -1:
            raise ValueError("bytes must be greater than 0 or -1")

        super().__init__()

        self.fh = open(path, mode)
        self.bytes = bytes

    def run(self):
        buff = self.fh.read(self.bytes)
        if buff:
            self.put(buff)
        else:
            self.fh.close()
            self.finish()


class FileSink(Element):
    allowed_modes = ("w", "wb", "a", "ab")

    def __init__(self, path=None, mode="wb"):
        if not path:
            raise ValueError("path not specified")

        if mode not in FileSink.allowed_modes:
            raise ValueError(f"mode must in one of {FileSink.allowed_modes}")

        super().__init__()

        self.fh = open(path, mode)

    def run(self):
        try:
            buff = self.get()
            self.fh.write(buff)
            return True

        except Empty:
            return False

        except EOF:
            self.fh.close()
            self.finish()
