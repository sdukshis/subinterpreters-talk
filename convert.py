import pickle
import array
from sys import version
import gensim.downloader as api

wv = api.load('word2vec-ruscorpora-300')

vectors_bytes = wv.get_normed_vectors().tobytes()

arr = array.array('f', vectors_bytes)

with open('word2vec-ruscorpa-300.pkl', 'wb') as fd:
    pickle.dump(arr, fd)
