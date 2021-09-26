import os
import pickle
import threading
import textwrap as tw
from multiprocessing import Pool

import pyperf

import _xxsubinterpreters

LIMIT = 200000
CPUS = os.cpu_count()

class SyncCounter():
    def __init__(self, initial=0):
        self._lock = threading.Lock()
        self._counter = initial
    
    def get(self):
        with self._lock:
            return self._counter

    def inc(self, val=1):
        with self._lock:
            prev_val = self._counter
            self._counter += val
        return prev_val

def isprime(n):
    if n < 2:
        return False
    
    for i in range(2, n):
        if n % i == 0:
            return False
    
    return True

class ExecThread(threading.Thread):
    def __init__(self, begin, end, step, total_result):
        super().__init__()
        self._begin = begin
        self._end = end
        self._step = step
        self._total_result = total_result

    def run(self):
        result = 0
        for i in range(self._begin, self._end, self._step):
            result += isprime(i)

        self._total_result.inc(result)

class SubInthread(threading.Thread):
    def __init__(self, begin, end, step, total_result):
        super().__init__()
        self._begin = begin
        self._end = end
        self._step = step
        self._total_result = total_result
        self._interp = _xxsubinterpreters.create()

    def run(self):
        chan_id = _xxsubinterpreters.channel_create()
        _xxsubinterpreters.run_string(self._interp, tw.dedent("""
            # import pickle
            import _xxsubinterpreters

            def isprime(n):
                if n < 2:
                    return False
                
                for i in range(2, n):
                    if n % i == 0:
                        return False
                
                return True
            
            result = 0;
            for i in range(begin, end, step):
                result += isprime(i)

            _xxsubinterpreters.channel_send(chan_id, result.to_bytes(8, 'big'))

        """), shared=dict(
                begin=self._begin,
                end=self._end,
                step=self._step,
                chan_id=chan_id,
        ))

        raw_result = _xxsubinterpreters.channel_recv(chan_id)
        _xxsubinterpreters.channel_release(chan_id)
        result = int.from_bytes(raw_result, 'big')
        self._total_result.inc(result)
        _xxsubinterpreters.destroy(self._interp)

def count_primes_sinlge():
    result = 0
    for n in range(2, LIMIT):
        result += isprime(n)
    
    return result

def count_primes_multithreading():
    total_result = SyncCounter(1)
    odds = [2*i + 1 for i in range(CPUS)]

    jobs = [ExecThread(odds[i], LIMIT, 2*CPUS, total_result) for i in range(CPUS)]
    for job in jobs:
        job.start()
    for job in jobs:
        job.join()
    return total_result.get()

def count_primes_subinterpreters():
    total_result = SyncCounter(1)
    odds = [2*i + 1 for i in range(CPUS)]

    jobs = [SubInthread(odds[i], LIMIT, 2*CPUS, total_result) for i in range(CPUS)]
    for job in jobs:
        job.start()
    for job in jobs:
        job.join()
    return total_result.get()

def count_primes_step(begin, end, step):
    result = 0
    for i in range(begin, end, step):
        result += isprime(i)
    
    return result

def count_primes_multiprocessing():
    odds = [2*i + 1 for i in range(CPUS)]
    with Pool(CPUS) as p:
       total_result = sum(p.starmap(count_primes_step, [(odds[i], LIMIT, 2*CPUS) for i in range(CPUS)]))
    return total_result + 1 # +1 for 2

def main():
    # print(count_primes_sinlge())
    # print(count_primes_multithreading())
    # print(count_primes_subinterpreters())
    # print(count_primes_multiprocessing())
    # runner = pyperf.Runner()
    # runner.bench_func("count_primes_single", count_primes_sinlge)
    # runner.bench_func("count_primes_multithreading", count_primes_multithreading)
    # runner.bench_func("count_primes_subinterpreters", count_primes_subinterpreters)
    # runner.bench_func("count_primes_multiprocessing", count_primes_multiprocessing)

if __name__ == "__main__":
    main()
