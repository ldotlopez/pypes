import unittest
from pypes import Pipeline
from pypes.elements import SampleSrc, StoreSink, \
    Transformer, Filter


class TestTransformer(Transformer):
    def transform(self, x):
        try:
            int(x)
            return x*2

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
        pipe = Pipeline()

        src, trans, sink = SampleSrc(sample=(1, 'a', 2)), TestTransformer(), StoreSink()
        pipe.connect_many(src, trans, sink)

        while pipe.run():
            pass

        self.assertEqual(sink.store, [2, 'a', 4])

    def test_filter(self):
        pipe = Pipeline()

        src, filt, sink = SampleSrc(sample=(1, 'a', 3, '8', 53, 22)), TestFilter(), StoreSink()
        pipe.connect_many(src, filt, sink)
        while pipe.run():
            pass

        self.assertEqual(sink.store, ['8', 22])

if __name__ == '__main__':
    unittest.main()
