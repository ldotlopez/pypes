import unittest
from pypes import Pipeline
from pypes.elements import SampleSrc, StoreSink, \
    Transformer, Filter, LambdaFilter, \
    HttpSrc, Soup


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
        src, trans, sink = SampleSrc(sample=[1, 'a', 2]), TestTransformer(), StoreSink()
        Pipeline().connect_many(src, trans, sink).execute()

        self.assertEqual(sink.store, [2, 'a', 4])

    def test_filter(self):
        src, filt, sink = SampleSrc(sample=[1, 'a', 3, '8', 53, 22]), TestFilter(), StoreSink()
        Pipeline().connect_many(src, filt, sink).execute()

        self.assertEqual(sink.store, ['8', 22])

    def test_soup(self):
        src, soup, store = HttpSrc(url='https://duckduckgo.com/html/?q=python'), Soup(selector='.results_links a.large'), StoreSink()
        Pipeline().connect_many(src, soup, store).execute()
        self.assertTrue(len(store.store) > 0)

    def test_lambda(self):
        src, filt, store = SampleSrc(sample=[1, 3, 5, 7, 11]), LambdaFilter(func=lambda x: x in (3, 5)), StoreSink()
        Pipeline().connect_many(src, filt, store).execute()
        self.assertEqual(store.store, [3, 5])


if __name__ == '__main__':
    unittest.main()
