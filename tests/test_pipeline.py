import unittest
from pypes import Pipeline, WriteError
from pypes.elements import SampleSrc, StoreSink, Tee, Adder


class TestPipeline(unittest.TestCase):
    def test_basic(self):
        src, sink = SampleSrc(sample=(1, 'a')), StoreSink()
        Pipeline().connect(src, sink).execute()

        self.assertEqual(sink.store, [1, 'a'])

    def test_adder(self):
        src, adder, sink = SampleSrc(sample=(1, 2, 3)), Adder(), StoreSink()
        Pipeline().connect_many(src, adder, sink).execute()

        self.assertEqual(sink.store, [2, 3, 4])

    def test_false_tee(self):
        src, tee, sink = SampleSrc(sample=(1, 2, 3)), Tee(1), StoreSink()

        pipe = Pipeline().connect(src, tee)
        pipe.connect(tee, sink, 'tee_00', 'default').execute()

        self.assertEqual(sink.store, [1, 2, 3])

    def test_tee(self):
        pipe = Pipeline()
        src = SampleSrc(sample=(1, 2, 3))
        tee = Tee(2)
        adder = Adder(amount=2)
        sink1, sink2 = StoreSink(), StoreSink()

        pipe.connect(src, tee)

        pipe.connect(tee, sink1, 'tee_00', 'default')
        pipe.connect(tee, adder, 'tee_01', 'default')

        pipe.connect(adder, sink2)

        #
        # Check write connections
        #

        # src -> tee
        src_to_tee = pipe.get_write_queue(src)
        self.assertIsNotNone(src_to_tee)

        # tee_00 -> sink1
        tee00_to_sink1 = pipe.get_write_queue(tee, 'tee_00')
        self.assertIsNotNone(tee00_to_sink1)

        # tee_01 -> adder
        tee01_to_adder = pipe.get_write_queue(tee, 'tee_01')
        self.assertIsNotNone(tee01_to_adder)

        # adder -> sink2
        adder_to_sink2 = pipe.get_write_queue(adder, 'default')
        self.assertIsNotNone(adder_to_sink2)

        # Check failure
        with self.assertRaises(WriteError):
            pipe.get_write_queue(tee, 'tee_02')

        #
        # Check read connections
        #

        # tee <- src
        tee_from_src = pipe.get_read_queue(tee)
        self.assertIsNotNone(tee_from_src)
        self.assertEqual(tee_from_src, src_to_tee)

        # sink1 <- tee_00
        sink1_from_tee00 = pipe.get_read_queue(sink1)
        self.assertIsNotNone(sink1_from_tee00)
        self.assertEqual(sink1_from_tee00, tee00_to_sink1)

        # adder <- tee_01
        adder_from_tee01 = pipe.get_read_queue(adder)
        self.assertIsNotNone(adder_from_tee01)
        self.assertEqual(adder_from_tee01, tee01_to_adder)

        # sink2 <- adder
        sink2_from_adder = pipe.get_read_queue(sink2)
        self.assertIsNotNone(sink2_from_adder)
        self.assertEqual(sink2_from_adder, adder_to_sink2)

        pipe.execute()

        self.assertEqual(sink1.store, [1, 2, 3])
        self.assertEqual(sink2.store, [3, 4, 5])

if __name__ == '__main__':
    unittest.main()
