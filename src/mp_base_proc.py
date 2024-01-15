#mp_base_proc.py    04Jan2024  crs Author
"""
Multiprocessing base process
Communication between base process to new process
Organizing communication but avoiding restriction
that can't pickle modules
"""
import time
import multiprocessing as mp

            
def new_proc():
    print("Inside New Process")        
    while True:
        print("Hi: new_proc")
        time.sleep(.5)

class MpBaseProc:
    """ Multiprocessing main process
    """
    def __init__(self, target):
        qlen = 4
        self.new_process = mp.Process(target=target)
        self.cmd_queue = mp.Queue(qlen)      # Commands from new process
        self.cmd_resp_queue = mp.Queue(qlen)
        print("Starting New Process")        
        self.new_process.start()

if __name__ == "__main__":
    """ Setup communication between base process and
    new process.
    :target_fun: target function in new process
    """

    bP = MpBaseProc(target=new_proc)
    time.sleep(2)
    while True:
        print("Hi from base process")
        time.sleep(.3)