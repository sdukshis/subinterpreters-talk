import pickle
import threading
import textwrap as tw

import gensim.downloader as api
from gensim.models import KeyedVectors
from memory_profiler import profile

import _xxsubinterpreters as subinterpreters

class InterpreterThread(threading.Thread):
    @profile
    def __init__(self, vocab, vectors_bytes):
        super().__init__()
        self._vocab = vocab
        self._vectors_bytes = vectors_bytes
        self._interp = subinterpreters.create()

    @profile
    def run(self):
        vocab_pkl = pickle.dumps(self._vocab)
        vectors_pkl = pickle.dumps(self._vectors_bytes, protocol=5)
        code = tw.dedent("""
            import pickle

            vocab = pickle.loads(vocab_pkl)
            # vectors = memoryview(vectors_bytes).cast('f')
            print(vocab[0])
            # print(vectors[0])
        """)
        subinterpreters.run_string(self._interp, code,
            shared={
                'vocab_pkl': vocab_pkl,
                'vectors_pkl': vectors_pkl,
            })
        subinterpreters.destroy(self._interp)

@profile
def main():
    # wv = KeyedVectors.load_word2vec_format('model.bin', binary=False)
    wv = api.load('word2vec-ruscorpora-300')

    vocab = wv.index_to_key
    vectors_bytes = wv.get_normed_vectors().tobytes()
    del wv # release memory
    interp = InterpreterThread(vocab, vectors_bytes)

    interp.start()
    interp.join()

if __name__ == "__main__":
    main()