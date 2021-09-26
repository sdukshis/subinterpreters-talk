def similarity(a, b):
    assert len(a) == len(b)
    n = len(a)
    result = 0
    for i in range(n):
        result += a[i] * b[i]
    return result

def get_vector_by_index(arr, pos, vector_size):
    begin = pos * vector_size
    end = (pos + 1) * vector_size
    return arr[begin:end]