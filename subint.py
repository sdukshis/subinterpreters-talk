import textwrap as tw
import pickle
import threading

import _xxsubinterpreters as interpreters
# interpid = interpreters.create()
# print('before')
# interpreters.run_string(interpid, 'print("during")')
# print('after')

interpid = interpreters.create()

interpreters.run_string(interpid, tw.dedent("""
    import pickle
    import _xxsubinterpreters as interpreters
"""))

channel_id = interpreters.channel_create()
def run(interpid, channel_id):
    interpreters.run_string(interpid, tw.dedent("""
        raw = interpreters.channel_recv(channel_id)
        if msg := pickle.loads(raw):
            print(f"{msg = }")
        interpreters.channel_release(channel_id)
        """),
        shared=dict(
            channel_id=channel_id,
            ),
        )
raw = pickle.dumps("Hello, world", protocol=5)
interpreters.channel_send(channel_id, raw)

t = threading.Thread(target=run, args=(interpid, channel_id))
t.start()
t.join()
