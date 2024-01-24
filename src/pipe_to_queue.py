#pipe_to_queue.py   23Jan2024  crs, Author
""" Convert PIPE output into queue
Initially to facilitate non-blocking reading
"""
from threading import Thread
import queue
import time

class PipeToQueue:
    """ Store Pipe output in a queue
    """
    def __init__(self, pipe):
        self.active = True  # Cleared when done
        self.pipe = pipe
        self.reader_queue = queue.Queue()
        self.thread_proc = Thread(target=self.reader_proc)
        self.thread_proc.start()
        
    def reader_proc(self):
        while self.active:
            if self.pipe is not None:
                rd = self.pipe.read()
                self.reader_queue.put(rd)
            else:
                print("reader_proc: waiting for pipe")
                time.sleep(.1)

    def stop(self):
        """ Stop reading
        """
        self.active = False
            
    def get(self):
        """ Return string since last read
        :returns: last read, "" if none
        """
        st = ""
        while not self.reader_queue.empty():
            rd =  self.reader_queue.get()
            if len(rd) == 0:
                break
            
            srd = rd.decode("utf-8")
            st += srd
        return st    
        
if __name__ == '__main__':
    import time
    import subprocess as sp
    from pipe_to_queue import PipeToQueue
    
    sp = sp.Popen('dir', stdout=sp.PIPE, shell=True)
    sto = PipeToQueue(sp.stdout)
    while True:
        so = sto.get()
        if so != "":
            print(so)
            print(50*"=")   # Separate non empty gets
          
        