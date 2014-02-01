import unittest
from pypes.queue import Queue, WritePad, ReadPad, \
    Empty, EOF, WriteError

class TestQueue(unittest.TestCase):
    def test_basic(self):
        queue = Queue()
        write = WritePad(queue)
        read = ReadPad(queue)

        for i in (1, 2, 3):
            write.put(i)

        r = read.flush()
 
        self.assertEqual(r, [1, 2, 3])


    def test_put_after_empty(self):
        queue = Queue()
        write = WritePad(queue)
        read = ReadPad(queue)

        write.put(1)
        write.put(2)
        r = read.flush()

        write.put(3)
        r += read.flush()

        self.assertEqual(r, [1, 2, 3])

    def test_read_error_after_gets(self):
        queue = Queue()
        write = WritePad(queue)
        read = ReadPad(queue)

        write.put(1)
        write.put(2)
        write.close()

        read.get()
        read.get()
        with self.assertRaises(EOF):
            read.get()

        with self.assertRaises(WriteError):
            write.put('x')

if __name__ == '__main__':
    unittest.main()
