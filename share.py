import pickle
import threading
import textwrap as tw
from multiprocessing.sharedctypes import Array
from multiprocessing import shared_memory, Process
from multiprocessing.managers import SharedMemoryManager
import array
from random import randrange
# import numpy as np

import pyperf
from memory_profiler import profile

import _xxsubinterpreters as subinterpreters

from helpers import similarity, get_vector_by_index

class InterpreterThread(threading.Thread):
    # @profile
    def __init__(self, buf, size, length, ntimes):
        super().__init__()
        self._buf = buf
        self._size = size
        self._length = length
        self._ntimes = ntimes
        self._interp = subinterpreters.create()

    # @profile
    def run(self):
        code = tw.dedent("""
            from random import randrange
            import sys
            sys.path.append('.')
            import fastint
            from helpers import similarity, get_vector_by_index

            mv = fastint.memviewfrombuffer(buf, length).cast('f')
            for i in range(ntimes):
                idx1 = randrange(0, length // 4 // size)
                idx2 = randrange(0, length //4 // size)
                v1 = get_vector_by_index(mv, idx1, size)
                v2 = get_vector_by_index(mv, idx2, size)
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

class InterpreterShmThread(threading.Thread):
    # @profile
    def __init__(self, shm_name, size, length, ntimes):
        super().__init__()
        self._shm_name = shm_name
        self._size = size
        self._length = length
        self._ntimes = ntimes
        self._interp = subinterpreters.create()

    # @profile
    def run(self):
        code = tw.dedent("""
            from random import randrange
            from multiprocessing import shared_memory
            import sys
            sys.path.append('.')
            from helpers import similarity, get_vector_by_index

            shm_a = shared_memory.SharedMemory(name=shm_name)
            arr = shm_a.buf.cast('f')
            for i in range(ntimes):
                idx1 = randrange(0, length // 4 // size)
                idx2 = randrange(0, length //4 // size)
                v1 = get_vector_by_index(arr, idx1, size)
                v2 = get_vector_by_index(arr, idx2, size)
                res = similarity(v1, v2)
            del v1
            del v2
            del arr
            shm_a.close()
        """)
        subinterpreters.run_string(self._interp, code,
            shared={
                'shm_name': self._shm_name,
                'size': self._size,
                'length': self._length,
                'ntimes': self._ntimes,
            })
        subinterpreters.destroy(self._interp)

# @profile
def bench_main(arr, size, length, ntimes):
    # @profile
    def bench_main_internal():
        for i in range(ntimes):
            idx1 = randrange(0, length // 4 // size)
            idx2 = randrange(0, length //4 // size)
            v1 = get_vector_by_index(arr, idx1, size)
            v2 = get_vector_by_index(arr, idx2, size)
            res = similarity(v1, v2)
    return bench_main_internal
    
def bench_subint(arr, size, length, ntimes):
    arr_buf, arr_size = arr.buffer_info()
    def bench_subint_internal():
        interp = InterpreterThread(arr_buf, size, length, ntimes)
        interp.start()
        interp.join()   
    return bench_subint_internal

def bench_subint_shm(shm_arr, size, length, ntimes):
    def bench_subint_internal():
        interp = InterpreterShmThread(shm_arr.name, size, length, ntimes)
        interp.start()
        interp.join()   
    return bench_subint_internal

def worker_mp(shm_name, size, length, ntimes):
    shm_a = shared_memory.SharedMemory(name=shm_name)
    arr = shm_a.buf.cast('f')
    for i in range(ntimes):
        idx1 = randrange(0, length // 4 // size)
        idx2 = randrange(0, length //4 // size)
        v1 = get_vector_by_index(arr, idx1, size)
        v2 = get_vector_by_index(arr, idx2, size)
        res = similarity(v1, v2)
    del v1
    del v2
    del arr
    shm_a.close()

def bench_mp(shm_arr, size, length, ntimes):
    def bench_mp_internal():
        p = Process(target=worker_mp, args=(shm_arr.name, size, length, ntimes))
        p.start()
        p.join()
    return bench_mp_internal

# @profile
def main():
    vector_size = 300
    ntimes = 100_000
    with open('word2vec-ruscorpa-300.pkl', 'rb') as fd:
        arr = pickle.load(fd)
    arr_size_bytes = arr.buffer_info()[1] * arr.itemsize
    with SharedMemoryManager() as smm:
        shm_arr = smm.SharedMemory(size=arr_size_bytes)
        shm_arr.buf[:arr_size_bytes] = memoryview(arr).cast('B')
        # bench_subint_shm(shm_arr, vector_size, arr_size_bytes, ntimes)()
        # bench_mp(shm_arr, vector_size, arr_size_bytes, ntimes)()
        runner = pyperf.Runner()
        runner.bench_func("MainInterpreter", bench_main(memoryview(arr), vector_size, arr_size_bytes, ntimes))
        runner.bench_func("SubInterpreterOverhead", bench_subint(arr, vector_size, arr_size_bytes, 0))
        runner.bench_func("SubInterpreter", bench_subint(arr, vector_size, arr_size_bytes, ntimes))
        # runner.bench_func("MultiprocessingOverhead", bench_mp(shm_arr, vector_size, arr_size_bytes, 0))
        runner.bench_func("Multiprocessing", bench_mp(shm_arr, vector_size, arr_size_bytes, ntimes))

if __name__ == "__main__":
    main()
