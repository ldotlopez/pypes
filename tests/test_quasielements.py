import unittest

# No exceptions from queue must be imported, if this occurs we are mixing layers 
from pypes.queue import Queue, WritePad, ReadPad

from pypes.element import SampleSrc, StoreSink, Done, NoInput

class TestQuasiElements(unittest.TestCase):
    def build_elements(self, sample):
        q = Queue()

        write = WritePad(q)
        read = ReadPad(q)

        src = SampleSrc(sample=sample)
        sink = StoreSink()

        src.output = write
        sink.input = read

        return q, write, read, src, sink


    def test_basic(self):
        q, write, read, src, sink = self.build_elements(sample=(1, 2, 3))

        # Check basic stuff
        src.run()
        src.run()
        src.run()
        self.assertEqual(q, [1, 2, 3])

        with self.assertRaises(Done):
            src.run()

    def test_empty(self):
        q, write, read, src, sink = self.build_elements(sample=(1, 2))

        # Push and pull [1]
        self.assertEqual(src.run(), True)
        self.assertEqual(sink.run(), True)
        self.assertEqual(sink.run(), False)

        # Push [2]
        self.assertEqual(src.run(), True)
        self.assertEqual(sink.run(), True)

    def test_eof(self):
        q, write, read, src, sink = self.build_elements(sample=(1, 2))

        self.assertEqual(src.run(), True)
        self.assertEqual(src.run(), True)
        with self.assertRaises(Done):
            src.run()

        self.assertEqual(sink.run(), True)
        self.assertEqual(sink.run(), True)

        # readpad raises EOF so element must raise Done
        with self.assertRaises(Done):
            sink.run()

        # src and writepad are done
        with self.assertRaises(Done):
            src.run()
        
if __name__ == '__main__':
    unittest.main()
