import sys
from multiprocessing import Process, Value, Lock

def is_prime(n):
    if n <= 1:
        return False
    if n <= 3: 
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False

    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def worker(limit, counter, total_result, lock):
    i = 2
    result = 0
    while i < limit:
        with lock:
            i = counter.value
            counter.value += 1
        if is_prime(i):
            result += 1

    with lock:
        total_result.value += result

if __name__ == "__main__":

    limit = int(sys.argv[1])
    nthreads = int(sys.argv[2])

    result = Value('i', 0)
    counter = Value('i', 0)
    lock = Lock()

    workers = [Process(target=worker, args=(limit, counter, result, lock)) for i in range(nthreads)]
 
    for w in workers:
        w.start()

    for w in workers:
        w.join()

    print(result.value)
