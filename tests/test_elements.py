import tempfile
import unittest

from pypes import Pipeline
from pypes.bs4 import Soup
from pypes.elements import (
    CustomFilter,
    Filter,
    HttpSrc,
    SampleSrc,
    StoreSink,
    Transformer,
)
from pypes.file import FileSink, FileSrc


class TestTransformer(Transformer):
    def transform(self, x):
        try:
            int(x)
            return x * 2

        except ValueError:
            return x


class TestFilter(Filter):
    def filter(self, x):
        try:
            as_int = int(x)
            return as_int % 2 == 0

        except ValueError:
            return False


class TestElements(unittest.TestCase):
    def test_transfomer(self):
        src, trans, sink = SampleSrc(sample=[1, "a", 2]), TestTransformer(), StoreSink()
        Pipeline().connect_many(src, trans, sink).execute()

        self.assertEqual(sink.packets, [2, "a", 4])

    def test_filter(self):
        src, filt, sink = (
            SampleSrc(sample=[1, "a", 3, "8", 53, 22]),
            TestFilter(),
            StoreSink(),
        )
        Pipeline().connect_many(src, filt, sink).execute()

        self.assertEqual(sink.packets, ["8", 22])

    def test_soup(self):
        src, soup, store = (
            HttpSrc(url="https://duckduckgo.com/html/?q=python"),
            Soup(selector=".results_links a.large"),
            StoreSink(),
        )
        Pipeline().connect_many(src, soup, store).execute()
        self.assertTrue(len(store.packets) > 0)

    def test_lambda(self):
        src, filt, store = (
            SampleSrc(sample=[1, 3, 5, 7, 11]),
            CustomFilter(func=lambda x: x in (3, 5)),
            StoreSink(),
        )
        Pipeline().connect_many(src, filt, store).execute()
        self.assertEqual(store.packets, [3, 5])

    def test_file(self):
        contents = "Hi, this is a test."

        t1 = tempfile.NamedTemporaryFile()
        t1.file.write(bytes(contents, "UTF-8"))
        t1.file.close()

        t2 = tempfile.NamedTemporaryFile()
        t2.file.close()

        Pipeline().connect_many(FileSrc(path=t1.name), FileSink(path=t2.name)).execute()

        with open(t2.name) as fh:
            self.assertEqual(fh.read(), contents)


if __name__ == "__main__":
    unittest.main()
