# From:
# http://eyalarubas.com/python-subproc-nonblock.html
#
# Eyal Arubas

from threading import Thread
from queue import Queue, Empty

class NonBlockingStreamReader:

    def __init__(self, stream):
        '''
        stream: the stream to read from.
                Usually a process' stdout or stderr.
        '''
        self._cont = True
        self._s = stream
        self._q = Queue()

        def _populateQueue(stream, queue: Queue):
            '''
            Collect lines from 'stream' and put them in 'queue'.
            '''

            while self._cont:
                line = stream.readline()
                if line:
                    queue.put(line)
                else:
                    if self._cont:
                        raise UnexpectedEndOfStream

        self._t = Thread(target = _populateQueue,
                args = (self._s, self._q))
        self._t.start() #start collecting lines from the stream

    def readline(self, timeout = None):
        try:
            return self._q.get(block = timeout is not None,
                    timeout = timeout)
        except Empty:
            return None
    
    def __del__(self) -> None:
        self._cont = False

class UnexpectedEndOfStream(Exception): pass