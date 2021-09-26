import multiprocessing
import os
import pyperf
import threading
import textwrap
import _xxsubinterpreters

CPUS = os.cpu_count()
n = 50_000
fact = 1
for i in range(1, n + 1):
    fact = fact * i
CODE = """
n = 50_000
fact = 1
for i in range(1, n + 1):
    fact = fact * i
"""


def worker_func(*args):
    exec(CODE)


class InterpreterThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self._interp = _xxsubinterpreters.create()

    def run(self):
        code = textwrap.dedent("""
        n = 50_000
        fact = 1
        for i in range(1, n + 1):
            fact = fact * i
        """)
        _xxsubinterpreters.run_string(self._interp, code)
        _xxsubinterpreters.destroy(self._interp)


class ExecThread(threading.Thread):
    def run(self):
        worker_func()


def run_threads(worker):
    jobs = [worker() for _ in range(CPUS)]
    for job in jobs:
        job.start()
    for job in jobs:
        job.join()

def bench_sequential():
    for _ in range(CPUS):
        exec(CODE)

def bench_threads():
    run_threads(ExecThread)

def bench_subinterpreters():
    run_threads(InterpreterThread)

def bench_mp():
    with multiprocessing.Pool(CPUS) as pool:
        pool.map(worker_func, [None] * CPUS)


def main():
    runner = pyperf.Runner()

    for bench, func in (
        ("Sequential", bench_sequential),
        ("Threads", bench_threads),
        ("Subinterpreters", bench_subinterpreters),
        ("Multiprocessing", bench_mp),
    ):
        bench = f"{bench} (CPUS={CPUS})"
        runner.bench_func(bench, func)


if __name__ == "__main__":
    main()
