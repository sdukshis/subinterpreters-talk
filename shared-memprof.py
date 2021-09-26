import pickle
import threading
import textwrap as tw
from multiprocessing.sharedctypes import Array
from multiprocessing import shared_memory, Process
from multiprocessing.managers import SharedMemoryManager
import array
from random import randrange

from memory_profiler import profile

import _xxsubinterpreters as subinterpreters

class InterpreterThread(threading.Thread):
    @profile
    def __init__(self, buf, size, length, ntimes):
        super().__init__()
        self._buf = buf
        self._size = size
        self._length = length
        self._ntimes = ntimes
        self._interp = subinterpreters.create()

    @profile
    def run(self):
        code = tw.dedent("""
            from random import randrange
            import sys
            sys.path.append('.')
            from helpers import similarity, get_vector_by_index

            vectors = memoryview(buf).cast('f')
            for i in range(ntimes):
                idx1 = randrange(0, length // 4 // size)
                idx2 = randrange(0, length //4 // size)
                v1 = get_vector_by_index(vectors, idx1, size)
                v2 = get_vector_by_index(vectors, idx2, size)
                res = similarity(v1, v2)
        """)
        subinterpreters.run_string(self._interp, code,
            shared={
                'buf': self._buf,
                'size': self._size,
                'length': self._length,
                'ntimes': self._ntimes,
            })
        subinterpreters.destroy(self._interp)

@profile
def main():
    vector_size = 300
    ntimes = 100_000
    with open('word2vec-ruscorpa-300.pkl', 'rb') as fd:
        arr = pickle.load(fd)
    arr_size_bytes = arr.buffer_info()[1] * arr.itemsize
    arr_bytes = arr.tobytes()
    interp = InterpreterThread(arr_bytes, vector_size, arr_size_bytes, ntimes)
    interp.start()
    interp.join()

if __name__ == "__main__":
    main()