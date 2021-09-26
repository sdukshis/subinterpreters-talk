import fastint
import array

raw = bytes(100*4)

arr = array.array('f', raw)
arr[10] = 42
print(arr.buffer_info())
buf, size = arr.buffer_info()

mv = fastint.memviewfrombuffer(buf, size * 4)
print(mv.cast('f')[10])
# print(fastint.add(10, 10))