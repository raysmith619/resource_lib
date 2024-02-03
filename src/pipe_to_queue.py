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
    newline = '\r\n'
    def __init__(self, pipe):
        self.active = True  # Cleared when done
        self.pipe = pipe
        self.reader_queue = queue.Queue()
        self.thread_proc = Thread(target=self.reader_proc)
        self.thread_proc.start()
        self.line_buf = ""      # excess after newline
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

    def get_line(self):
        """ Get next line, less newline, any remaining
        is stored in self.line_buf to be added next call
        stores 
        :returns: line (less newline) "" if none
        """
        st = self.line_buf
        if PipeToQueue.newline not in st:
            st += self.get()
        idx = st.find(PipeToQueue.newline)
        if idx == -1:
            self.line_buf = st
            return ""
        
        line = st[:idx]
        self.line_buf = st[idx+len(PipeToQueuenewline):]    # After newline
        return line
                
if __name__ == '__main__':
    import time
    import subprocess as sp
    from pipe_to_queue import PipeToQueue
    
    sp = sp.Popen('dir', stdout=sp.PIPE, shell=True)
    sto = PipeToQueue(sp.stdout)
    ln = 0
    while True:
        so = sto.get_line()
        if so != "":
            ln += 1
            print(ln, so)
          
        