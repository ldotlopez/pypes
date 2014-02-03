import unittest
from pypes import Pipeline
from pypes.elements import SampleSrc, StoreSink, Tee, Adder


class TestPipeline(unittest.TestCase):
    def test_basic(self):
        pipe = Pipeline()

        src, sink = SampleSrc(sample=(1,'a')), StoreSink()
        pipe.connect(src, sink)
        while pipe.run():
            pass

        self.assertEqual(sink.store, [1, 'a'])

    def test_adder(self):
        pipe = Pipeline()
        src, adder, sink = SampleSrc(sample=(1,2, 3)), Adder(), StoreSink()

        pipe.connect(src, adder)
        pipe.connect(adder, sink)

        while pipe.run():
            pass

        self.assertEqual(sink.store, [2, 3, 4])

    def test_false_tee(self):
        pipe = Pipeline()
        src, tee, sink = SampleSrc(sample=(1, 2, 3)), Tee(1), StoreSink()

        pipe.connect(src, tee)
        pipe.connect(tee, sink)

        while pipe.run():
            pass

        self.assertEqual(sink.store, [1, 2, 3])

if __name__ == '__main__':
    unittest.main()
